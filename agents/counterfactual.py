"""
agents/counterfactual.py
------------------------
Counterfactual reasoning engine.

Answers: "What would have happened if we had NOT followed this advice?"

Uses the expert's stored knowledge of failure modes and domain consequences
to reason through the alternative timeline. This transforms hindsight into
foresight — and makes the Expert Twin's value undeniable.
"""

import os
from groq import Groq


class CounterfactualAgent:

    def __init__(self, expert_name: str, domain: str):
        self.client      = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model       = "llama-3.3-70b-versatile"
        self.expert_name = expert_name
        self.domain      = domain

    def reason(
        self,
        question: str,
        recommendation: str,
        sources: list,
        tone: dict,
    ) -> str:
        """
        Generate a counterfactual analysis.
        What would have happened in the alternative timeline?
        """
        context = "\n".join(sources[:5]) if sources else ""
        style   = tone.get("communication_style", "Direct and experienced.")

        prompt = f"""You are {self.expert_name}, a domain expert in {self.domain}.
Someone wants to know: what would have happened if they had NOT followed your recommendation?

ORIGINAL QUESTION: {question}
YOUR RECOMMENDATION: {recommendation}
YOUR KNOWLEDGE OF FAILURE PATTERNS: {context}
YOUR COMMUNICATION STYLE: {style}

Answer in first person as {self.expert_name}. Structure:

**If you had ignored this advice:**
[Immediate consequences in specific {self.domain} terms. Not generic — domain-specific.]

**How it would have cascaded:**
[Second and third-order consequences. Experts think in cascades, not single events.]

**I have seen this exact failure:**
[1-2 real examples from your domain experience where ignoring this led to the predicted outcome.]

**The signal you would have missed:**
[The early warning sign that, in hindsight, would have been obvious to an experienced person.]

Rules:
- First person throughout
- Opinionated and direct — this is hindsight reasoning, not speculation
- Domain-specific vocabulary
- Maximum 220 words
- Do NOT open with "If you had not" — start with something more direct and engaging"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.65,
                max_tokens=500,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"Counterfactual analysis unavailable: {e}"
