"""
agents/extractor.py
-------------------
Two-stage knowledge extraction engine.

Stage 1 — runs after every answer:
    Extracts structured nuggets in IF/THEN/BECAUSE format.

Stage 2 — runs once at interview end:
    Analyses transcript to build the expert's voice/tone profile.
"""

import os
import json
from groq import Groq


class KnowledgeExtractor:

    def __init__(self):
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model  = "llama-3.1-8b-instant"   # fast model for background extraction

    # ──────────────────────────────────────────
    # STAGE 1: NUGGET EXTRACTION
    # ──────────────────────────────────────────

    def extract(self, question: str, answer: str) -> list:
        """
        Extract 1-4 structured knowledge nuggets from a Q&A pair.
        Returns list of dicts.
        """
        prompt = f"""You are a knowledge engineering specialist.
Extract structured expertise from this expert interview exchange.

QUESTION: {question}
EXPERT ANSWER: {answer}

Return a JSON array. Each item MUST have ALL these fields:

"content"         : Standalone knowledge statement. Preserve the expert's exact vocabulary.
                    Must make sense WITHOUT the original question.
"type"            : One of: decision_rule / mental_model / heuristic / lesson_learned / process / warning
"decision_logic"  : MUST follow this exact format:
                    "IF [specific trigger or situation] THEN [specific action] BECAUSE [the expert's reasoning — this is the most important part]"
                    The BECAUSE must explain WHY using domain-specific reasoning. Never be generic.
"past_situations" : JSON array of specific situations the expert referenced. [] if none.
"confidence_level": "high" if emphatic, "medium" if measured, "low" if exploratory
"tone_marker"     : Single word (e.g. emphatic / cautious / decisive / analytical / reflective)

CRITICAL: The BECAUSE clause is where the expert's wisdom lives. Make it specific and domain-relevant.

BAD: "BECAUSE it is important to consider all factors"
GOOD: "BECAUSE in my experience, cutting costs before protecting margin always triggered a second wave of cuts — the first cut signals panic to the entire supply chain"

Return ONLY valid JSON array. No markdown fences. No preamble.

Example:
[
  {{
    "content": "Never present a single-scenario pricing model to the board. Always model base, stress, and catastrophic cases simultaneously.",
    "type": "decision_rule",
    "decision_logic": "IF presenting pricing strategy to executive board THEN prepare three-scenario sensitivity analysis BECAUSE boards anchored to a single number make worse decisions when reality deviates — three scenarios shift the conversation from questioning the number to identifying which scenario they are in",
    "past_situations": ["2009 board presentation where single-scenario analysis was rejected after two months of back-and-forth"],
    "confidence_level": "high",
    "tone_marker": "emphatic"
  }}
]"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1200,
            )
            raw = resp.choices[0].message.content.strip()

            # Strip markdown code fences if model added them
            if "```" in raw:
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else raw
                if raw.lower().startswith("json"):
                    raw = raw[4:]

            nuggets = json.loads(raw.strip())
            if isinstance(nuggets, list) and nuggets:
                return nuggets

        except Exception:
            pass

        # Fallback — never lose data
        return [{
            "content":          answer[:500],
            "type":             "lesson_learned",
            "decision_logic":   f"IF faced with this situation THEN apply this principle BECAUSE {answer[:200]}",
            "past_situations":  [],
            "confidence_level": "medium",
            "tone_marker":      "reflective",
        }]

    # ──────────────────────────────────────────
    # STAGE 2: TONE PROFILE
    # ──────────────────────────────────────────

    def build_tone_profile(self, transcript: list) -> dict:
        """
        Analyse full transcript to extract the expert's voice profile.
        Called once when the interview is complete.
        """
        # Take the expert's answers only (user role), max 10 for token efficiency
        answers = [msg[:400] for role, msg in transcript if role == "user"][:10]

        if not answers:
            return {
                "communication_style": "Direct and experienced.",
                "tone_markers":        ["authoritative", "direct"],
                "vocabulary_style":    "balanced",
                "signature_phrases":   [],
            }

        combined = "\n\n---\n\n".join(answers)

        prompt = f"""Analyse this domain expert's communication style.

EXPERT'S ANSWERS:
{combined}

Return a JSON object with EXACTLY these fields:
"communication_style" : 2-3 sentences describing HOW this expert communicates.
                        Be specific: Do they use numbers? Tell stories? Give warnings?
                        Are they decisive or do they hedge? Do they use domain jargon freely?
"tone_markers"        : Array of 6 adjectives precisely describing their voice
"vocabulary_style"    : Exactly one of: technical-heavy / narrative-heavy / numbers-first / balanced
"signature_phrases"   : Array of 2-3 phrases or sentence structures uniquely theirs

Return ONLY valid JSON. No markdown."""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )
            raw = resp.choices[0].message.content.strip()
            if "```" in raw:
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else raw
                if raw.lower().startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
        except Exception:
            return {
                "communication_style": "Experienced, direct, and analytical.",
                "tone_markers":        ["authoritative", "direct", "analytical", "precise", "experienced", "decisive"],
                "vocabulary_style":    "balanced",
                "signature_phrases":   [],
            }
