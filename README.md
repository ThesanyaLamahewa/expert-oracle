# 🧠 Expert Oracle — Knowledge Immortalization Agent

> *"The expert never truly retires."*

A Decision Intelligence System that preserves irreplaceable human expertise through structured AI interviews, then makes it permanently queryable as an Expert Twin.

---

## The Problem

Every year, organisations lose billions in institutional knowledge when senior experts retire or leave. This knowledge — the decision logic, mental models, and hard-won heuristics — never makes it into any document or system.

**Expert Oracle solves this.**

## What It Does

| Stage | Description |
|-------|-------------|
| 🎤 **Interview** | AI agent conducts structured knowledge-extraction interviews, probing for the *reasoning* behind every decision |
| ⚙️ **Extract** | Every answer is decomposed into `IF → THEN → BECAUSE` decision logic with confidence levels and past situations |
| 🧠 **Expert Twin** | Answers questions in the expert's own voice — opinionated, experience-grounded, citing past situations |
| ⚠️ **Counterfactual** | Reasons through "what would have happened if we hadn't followed this advice?" |

## Tech Stack (100% Free)

- **LLM:** Groq API (llama-3.3-70b-versatile + llama-3.1-8b-instant) — free tier
- **Memory:** ChromaDB — local vector database, no cost
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2) — runs locally, free
- **Framework:** LangChain — free
- **UI:** Streamlit — free

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/expert-oracle.git
cd expert-oracle

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install packages
pip install -r requirements.txt

# 4. Create .env file
echo GROQ_API_KEY=your_key_here > .env

# 5. Run
streamlit run app.py
```

Get your free Groq API key at: https://console.groq.com

## Key Features

- **Structured decision logic** — IF/THEN/BECAUSE format preserves reasoning, not just conclusions
- **Tone replication** — voice profile built from interview transcript ensures the twin sounds like the expert
- **Explanation layer** — every recommendation includes "I recommend X *because* in similar situations I have seen..."
- **Counterfactual engine** — reasons through the alternative timeline to demonstrate the value of expert judgment
- **Episodic memory** — past situations are indexed and retrieved as evidence for future recommendations

## Assignment Context

Built for: BSc Applied Data Science Communication — Assignment II  
Course: Data Science Applications and AI [LB3114]  
Institution: General Sir John Kotelawala Defence University

---

*Real pain addressed: $4.1 trillion in institutional knowledge lost annually to workforce transitions.*
