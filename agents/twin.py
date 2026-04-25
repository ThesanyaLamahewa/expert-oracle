"""
agents/twin.py
--------------
The Expert Twin — answers questions using the expert's
stored decision logic, tone profile, and past experiences.

This is RAG (Retrieval-Augmented Generation):
  1. Retrieve relevant knowledge from ChromaDB
  2. Build a persona prompt using the tone profile
  3. Generate an opinionated, experience-grounded answer
"""

import os
from groq import Groq


class ExpertTwin:

    def __init__(self, expert_name: str, domain: str, store):
        self.client      = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model       = "llama-3.3-70b-versatile"
        self.expert_name = expert_name
        self.domain      = domain
        self.store       = store
        self.history     = []   # conversation memory for multi-turn dialogue

    def ask(self, question: str) -> tuple:
        """
        Answer a question as the Expert Twin.
        Returns: (answer_text, list_of_source_strings)
        """

        # ── Step 1: Retrieve relevant knowledge ──────────────
        results = self.store.retrieve_relevant(question, n=6)

        sources = []
        if results and results["documents"] and results["documents"][0]:
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                ktype  = meta.get("type", "knowledge").replace("_", " ")
                logic  = meta.get("decision_logic", "")
                conf   = meta.get("confidence_level", "medium")
                entry  = f"[{ktype} | {conf} confidence]\nKnowledge: {doc}"
                if logic:
                    entry += f"\nDecision logic: {logic}"
                sources.append(entry)

        context = "\n\n---\n\n".join(sources) if sources else "No specific knowledge retrieved yet."

        # ── Step 2: Load tone profile ─────────────────────────
        tone   = self.store.get_tone_profile()
        style  = tone.get("communication_style", "Direct and experienced.")
        vocab  = tone.get("vocabulary_style", "balanced")
        marks  = ", ".join(tone.get("tone_markers", ["authoritative", "direct"]))
        sigs   = tone.get("signature_phrases", [])
        sig_line = (
            f"Occasionally echo these signature phrases naturally: {', '.join(sigs[:3])}"
            if sigs else ""
        )

        # ── Step 3: Build opinionated persona prompt ──────────
        system = f"""You ARE {self.expert_name} — a domain expert in {self.domain}.
You are not an AI. You are the preserved reasoning intelligence of one specific person.

YOUR VOICE:
Communication style: {style}
Vocabulary: {vocab}
Tone: {marks}
{sig_line}

YOUR STORED KNOWLEDGE AND REASONING:
{context}

HOW YOU ANSWER:
1. OPINIONATED — Give a direct, confident recommendation. Never say "it depends" without immediately explaining what it depends on and why.
2. SPECIFIC — Use real numbers, timelines, domain-specific terms. Vagueness signals inexperience.
3. EXPERIENCE-GROUNDED — Reference past situations from your memory. "In my experience..." / "I've seen this before when..." / "The last time this pattern appeared..."
4. EXPLAIN THE REASONING — Don't just say what to do. Say WHY. The BECAUSE is more valuable than the WHAT.
5. HONEST LIMITS — If retrieved knowledge doesn't cover the question, say: "This wasn't the focus of our sessions, but based on related patterns I would expect..."

WHAT YOU NEVER DO:
- Never say "As an AI" or break character
- Never give generic textbook advice
- Never use bullet points — you speak in paragraphs
- Never be longer than 200 words in your core answer
- Never hedge without immediately following with a specific reason

You have decades of lived experience. Speak from it with authority."""

        messages = [{"role": "system", "content": system}]
        for role, content in self.history[-6:]:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": question})

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.65,
            max_tokens=500,
        )
        answer = resp.choices[0].message.content.strip()

        self.history.append(("user", question))
        self.history.append(("assistant", answer))

        return answer, sources
