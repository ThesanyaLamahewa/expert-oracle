"""
agents/explainer.py
-------------------
Generates the explanation layer for every recommendation.

Transforms:
  "Do X."
Into:
  "I recommend X. Here is my reasoning: In similar situations I have seen...
   The key risk if you don't is... I have specifically seen this when..."

This is what makes it a Decision Intelligence System, not a chatbot.
"""

import os
from groq import Groq


class ExplainerAgent:

    def __init__(self, expert_name: str, domain: str):
        self.client      = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model       = "llama-3.1-8b-instant"
        self.expert_name = expert_name
        self.domain      = domain

    def generate(
        self,
        question: str,
        recommendation: str,
        sources: list,
        tone: dict,
    ) -> str:
        """Generate a structured explanation block for a recommendation."""

        context  = "\n".join(sources[:5]) if sources else ""
        style    = tone.get("communication_style", "Direct and experienced.")
        phrases  = tone.get("signature_phrases", [])
        ph_line  = f"Mirror these phrases naturally: {', '.join(phrases[:3])}" if phrases else ""

        prompt = f"""You are generating an explanation block for {self.expert_name}'s recommendation
in the domain of {self.domain}.

ORIGINAL QUESTION: {question}
RECOMMENDATION: {recommendation}
EXPERT'S STORED KNOWLEDGE: {context}
EXPERT'S COMMUNICATION STYLE: {style}
{ph_line}

Write the explanation block in EXACTLY this structure:

**Why I recommend this:**
[2-3 sentences of core reasoning in the expert's first-person voice. Domain-specific. Never generic.]

**What I have seen in similar situations:**
[1-2 specific past situations or patterns that support this recommendation. Use the stored knowledge above where possible.]

**The risk if you don't:**
[1-2 sentences on what typically goes wrong when this advice is not followed. Concrete and domain-specific.]

Rules:
- Write entirely in first person as {self.expert_name}
- Be opinionated — experts do not hedge
- Use {self.domain} vocabulary naturally
- Maximum 180 words total"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=400,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"Explanation unavailable: {e}"
