"""
agents/conflict_detector.py
----------------------------
Knowledge Conflict Detector — Feature 4

Scans all stored knowledge nuggets, identifies pairs that are
semantically similar (same topic) but potentially contradictory
in their recommendations or reasoning.

Uses ChromaDB's similarity search to find candidate pairs,
then asks Groq to judge whether a genuine contradiction exists.

No new packages required — uses ChromaDB and Groq already installed.
"""

import os
import json
from groq import Groq


class ConflictDetector:
    """
    Detects semantic contradictions in the knowledge base.

    Strategy:
    1. For every stored nugget, retrieve the 3 most similar nuggets
    2. For each similar pair, ask Groq: do these genuinely contradict?
    3. Collect confirmed contradictions with explanation
    4. Return structured conflict report
    """

    def __init__(self, expert_name: str, domain: str):
        self.client      = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model       = "llama-3.1-8b-instant"
        self.expert_name = expert_name
        self.domain      = domain

    def scan(self, store) -> list:
        """
        Full contradiction scan across the knowledge base.

        Returns a list of conflict dicts:
        {
            "nugget_a":     str,   — first knowledge statement
            "nugget_b":     str,   — second knowledge statement
            "logic_a":      str,   — decision logic of first
            "logic_b":      str,   — decision logic of second
            "source_a":     str,   — where nugget A came from
            "source_b":     str,   — where nugget B came from
            "type_a":       str,   — knowledge type of A
            "type_b":       str,   — knowledge type of B
            "explanation":  str,   — how they contradict
            "resolution":   str,   — how the twin should handle this
            "severity":     str,   — high / medium / low
        }
        """
        conflicts   = []
        seen_pairs  = set()

        # Get all stored knowledge
        all_k = store.get_all()
        if not all_k["documents"] or len(all_k["documents"]) < 2:
            return []

        documents = all_k["documents"]
        metadatas = all_k["metadatas"]
        ids       = all_k["ids"]

        # For each nugget, find its most semantically similar neighbours
        for i, (doc, meta, doc_id) in enumerate(zip(documents, metadatas, ids)):

            # Retrieve similar nuggets
            results = store.retrieve_relevant(doc, n=4)

            if not results["documents"] or not results["documents"][0]:
                continue

            for j, (similar_doc, similar_meta) in enumerate(
                zip(results["documents"][0], results["metadatas"][0])
            ):
                # Skip self-matches
                if similar_doc == doc:
                    continue

                # Create a canonical pair key to avoid duplicate checks
                pair_key = tuple(sorted([doc[:80], similar_doc[:80]]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                # Ask Groq if this pair is contradictory
                conflict = self._judge_contradiction(
                    nugget_a=doc,
                    nugget_b=similar_doc,
                    meta_a=meta,
                    meta_b=similar_meta,
                )

                if conflict:
                    conflicts.append(conflict)

                # Cap at 12 conflicts for performance
                if len(conflicts) >= 12:
                    return conflicts

        return conflicts

    def _judge_contradiction(
        self,
        nugget_a: str,
        nugget_b: str,
        meta_a: dict,
        meta_b: dict,
    ) -> dict:
        """
        Ask Groq to determine if two similar nuggets genuinely contradict.
        Returns a conflict dict if contradiction found, None otherwise.
        """
        logic_a  = meta_a.get("decision_logic", "")
        logic_b  = meta_b.get("decision_logic", "")
        source_a = meta_a.get("source_question", "interview")
        source_b = meta_b.get("source_question", "interview")
        type_a   = meta_a.get("type", "knowledge")
        type_b   = meta_b.get("type", "knowledge")

        prompt = f"""You are a knowledge consistency analyst reviewing an expert's knowledge base.

EXPERT: {self.expert_name}
DOMAIN: {self.domain}

Examine these two knowledge statements from the same expert:

STATEMENT A:
Content: {nugget_a}
Decision logic: {logic_a}
Source: {source_a}

STATEMENT B:
Content: {nugget_b}
Decision logic: {logic_b}
Source: {source_b}

Your task: Determine if these two statements GENUINELY CONTRADICT each other.

A genuine contradiction means:
- They address the same or very similar situation
- They recommend opposite or incompatible actions
- Following both at the same time would be impossible or counterproductive

NOT a contradiction:
- They address different situations
- One is more specific than the other
- They are complementary perspectives on the same topic

Return a JSON object with EXACTLY these fields:
"is_contradiction": true or false
"severity": "high" (directly opposing advice) / "medium" (partially conflicting) / "low" (subtle tension) — only if is_contradiction is true, otherwise ""
"explanation": If contradiction: 1-2 sentences explaining HOW they contradict. If not: ""
"resolution": If contradiction: How the expert should reconcile this — e.g. "Apply Statement A when X, Statement B when Y" or "Statement B likely represents updated thinking". If not: ""

Return ONLY valid JSON. No markdown. No preamble."""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=400,
            )
            raw = resp.choices[0].message.content.strip()

            if "```" in raw:
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else raw
                if raw.lower().startswith("json"):
                    raw = raw[4:]

            result = json.loads(raw.strip())

            if result.get("is_contradiction") and result.get("explanation"):
                return {
                    "nugget_a":    nugget_a,
                    "nugget_b":    nugget_b,
                    "logic_a":     logic_a,
                    "logic_b":     logic_b,
                    "source_a":    source_a[:100],
                    "source_b":    source_b[:100],
                    "type_a":      type_a,
                    "type_b":      type_b,
                    "explanation": result.get("explanation", ""),
                    "resolution":  result.get("resolution", ""),
                    "severity":    result.get("severity", "medium"),
                }

        except Exception:
            pass

        return None