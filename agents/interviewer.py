"""
agents/interviewer.py
---------------------
Conducts a structured knowledge-extraction interview.

Goal: Surface the REASONING behind every decision — the tacit
knowledge that never makes it into documents.
"""

import os
from groq import Groq


class InterviewerAgent:

    def __init__(self):
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model   = "llama-3.3-70b-versatile"
        self.history = []
        self.expert_name = ""
        self.domain      = ""

    def start_interview(self, expert_name: str, domain: str) -> str:
        self.expert_name = expert_name
        self.domain      = domain
        self.history     = []

        system = f"""You are a world-class knowledge interviewer.
Your mission: extract the tacit expertise of {expert_name}, a domain expert in {domain}.

You want the REASONING, not just facts. Every answer should uncover:
- WHY they made certain decisions
- What warning signs they recognise that others miss
- Real situations where things went right and wrong
- The mental models they use unconsciously

RULES:
- Ask exactly ONE focused question per message
- Always probe for specific examples: "Can you give me a real situation?"
- Always probe for reasoning: "Why did you approach it that way?"
- Challenge vague answers gently: "Can you make that more specific?"
- Never let "it depends" go unchallenged: "It depends on what exactly?"

INTERVIEW ARC (follow naturally):
Turns 1-2:  Career journey and domain overview
Turns 3-4:  Hardest decisions and their reasoning
Turns 5-6:  Mental models and thinking frameworks
Turns 7-8:  Failure patterns and warning signs
Turns 9-10: Rules of thumb and heuristics
Turns 11+:  Lessons they wish they'd known earlier

Be warm, genuinely curious, and make the expert feel their knowledge is precious."""

        self.history.append({"role": "system", "content": system})

        opening = (
            f"Hello {expert_name}, thank you for doing this. "
            f"Your experience in {domain} represents knowledge that most organisations "
            f"never manage to capture — and we want to change that.\n\n"
            f"Let's start at the beginning: How did you first get into {domain}, "
            f"and what was the moment you realised you were thinking about it "
            f"differently from most people around you?"
        )
        self.history.append({"role": "assistant", "content": opening})
        return opening

    def respond(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            temperature=0.7,
            max_tokens=350,
        )
        reply = resp.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def get_transcript(self) -> list:
        """Return list of (role, message) for all non-system turns."""
        return [
            (m["role"], m["content"])
            for m in self.history
            if m["role"] in ("user", "assistant")
        ]
