from __future__ import annotations

import json
import re

from .errors import LLMError
from .llm import LLMService
from .prompts.templates import ANALYSIS_PROMPT, INSIGHTS_PROMPT, VIVA_PROMPT
from .repository import Repository

ANALYSIS_FIELDS = ["title", "authors", "publication_information", "summary", "research_problem", "objectives", "methodology", "dataset", "algorithms_models", "key_contributions", "results", "limitations", "future_work"]
MISSING = "Not explicitly stated in the paper."


def _json_response(text: str) -> object:
    candidate = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Gemini sometimes drops closing braces; try fixing common issues
        fixed = re.sub(r",\s*([}\]])", r"\1", candidate)  # trailing commas
        fixed = re.sub(r"(\}\s*),\s*", r"\1, ", fixed)  # normalize comma placement
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass
        # Last resort: extract JSON from the response
        match = re.search(r"\{.*\}", candidate, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        raise LLMError("The AI service returned an invalid structured response. Please try again.")


class GenerationService:
    def __init__(self, repository: Repository, llm: LLMService) -> None:
        self.repository, self.llm = repository, llm

    def _context(self, paper_id: str, per_section: int = 2) -> str:
        """Provide broad section coverage without overflowing a single LLM request."""
        selected = []
        counts: dict[str, int] = {}
        for chunk in self.repository.chunks_for(paper_id):
            allowed = 4 if chunk.section == "Unclassified" else per_section
            if counts.get(chunk.section, 0) < allowed:
                selected.append(chunk)
                counts[chunk.section] = counts.get(chunk.section, 0) + 1
        chunks = selected
        return "\n\n".join(f"[Page {chunk.page_number} | {chunk.section}]\n{chunk.text}" for chunk in chunks)

    def analyze(self, paper_id: str) -> dict[str, str]:
        result = _json_response(self.llm.generate(ANALYSIS_PROMPT.format(context=self._context(paper_id))))
        if not isinstance(result, dict):
            raise LLMError("The AI service returned an invalid analysis response. Please try again.")
        analysis = {field: str(result.get(field) or MISSING) for field in ANALYSIS_FIELDS}
        self.repository.save_json("analyses", paper_id, analysis)
        return analysis

    def analysis(self, paper_id: str) -> dict[str, str] | None:
        result = self.repository.load_json("analyses", paper_id)
        return result if isinstance(result, dict) else None

    def viva(
        self,
        paper_id: str,
    ) -> dict[str, list[dict[str, str]]]:

        result = _json_response(
            self.llm.generate(
                VIVA_PROMPT.format(
                    context=self._context(paper_id)
                ),
                temperature=0.3,
            )
        )

        expected = [
            "Basic",
            "Technical",
            "Methodology",
            "Results",
            "Research",
        ]

        if (
            not isinstance(result, dict)
            or any(
                key not in result
                or not isinstance(result[key], list)
                for key in expected
            )
        ):
            raise LLMError(
                "The AI service returned invalid viva questions. "
                "Please try again."
            )

        viva = {}

        for key in expected:
            entries = [
                {
                    "question": str(
                        item.get(
                            "question",
                            "Not explicitly stated in the paper.",
                        )
                    ),
                    "answer": str(
                        item.get(
                            "answer",
                            "Not explicitly stated in the paper.",
                        )
                    ),
                }
                for item in result[key]
                if isinstance(item, dict)
            ]

            viva[key] = entries[:4]

        self.repository.save_json(
            "viva",
            paper_id,
            viva,
        )

        return viva

    def stored_viva(self, paper_id: str) -> dict[str, list[dict[str, str]]] | None:
        result = self.repository.load_json("viva", paper_id)
        return result if isinstance(result, dict) else None

    def comparison(self, paper_ids: list[str]) -> dict[str, dict[str, str]]:
        fields = {"Research Problem": "research_problem", "Dataset": "dataset", "Methodology": "methodology", "Algorithms / Models": "algorithms_models", "Results": "results", "Limitations": "limitations", "Future Work": "future_work"}
        papers = {paper_id: self.repository.paper(paper_id) for paper_id in paper_ids}
        analyses = {paper_id: self.analysis(paper_id) for paper_id in paper_ids}
        return {label: {papers[paper_id].title if papers[paper_id] else paper_id: str((analyses[paper_id] or {}).get(field, MISSING)) for paper_id in paper_ids} for label, field in fields.items()}

    def insights(self, paper_ids: list[str]) -> dict[str, list[str]]:
        analyses = {self.repository.paper(paper_id).title: self.analysis(paper_id) for paper_id in paper_ids if self.repository.paper(paper_id)}
        if len(analyses) < 2 or any(value is None for value in analyses.values()):
            raise ValueError("Generate an analysis for at least two papers before requesting research insights.")
        output = _json_response(self.llm.generate(INSIGHTS_PROMPT.format(analyses=json.dumps(analyses))))
        if not isinstance(output, dict):
            raise LLMError("The AI service returned invalid research insights. Please try again.")
        insight = {"common_observations": [str(x) for x in output.get("common_observations", [])], "possible_research_directions": [str(x) for x in output.get("possible_research_directions", [])]}
        self.repository.save_json("insights", ",".join(sorted(paper_ids)), insight)
        return insight
