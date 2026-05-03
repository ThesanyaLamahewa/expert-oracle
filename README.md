# Expert Oracle - Knowledge Immortalization Agent

<div align="center">

> *"The expert never truly retires."*

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://expert-oracle-aerubfuwm454utwxysfcvd.streamlit.app/)
[![YouTube Demo](https://img.shields.io/badge/▶_Video_Demo-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/TVtIvns8BFU)
[![GitHub](https://img.shields.io/badge/Source_Code-GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ThesanyaLamahewa/expert-oracle)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.x-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq_API-llama--3.3--70b-F55036?style=flat-square)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-6C3FD6?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**A Multi-Agent Decision Intelligence System that preserves irreplaceable human expertise through structured AI interviews, then makes it permanently queryable as an Expert Twin.**

</div>

---

## Table of Contents

- [The Problem](#-the-problem)
- [Solution Overview](#-solution-overview)
- [Live Demo](#-live-demo)
- [System Architecture](#-system-architecture)
- [Agent Pipeline](#-agent-pipeline)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Usage Guide](#-usage-guide)

---

## The Problem

Every year, organisations lose billions in institutional knowledge when senior experts retire, resign, or transition roles. The decision logic, mental models, crisis heuristics, and hard-won experiential wisdom the very things that distinguish expert judgment from novice analysis never make it into any document or system.

**Consider this scenario:**

> *Friday 5pm. Dr. Margaret Chen - Senior Financial Analyst, 25 years, three recessions survived - clears her desk and retires. With her goes every pricing instinct, every crisis heuristic, every "I've seen this before" that no meeting, no document, no knowledge base ever captured.*
>
> *Monday 9am. The board faces a pricing crisis. Raw materials up 34%. A competitor just cut prices 12%. The new analysts have models. They don't have judgment.*
>
> **What if they could still ask Margaret?**

The global cost of this problem is estimated at **$4.1 trillion in institutional knowledge lost annually** to workforce transitions. Expert Oracle directly addresses this gap.

---

##  Solution Overview

Expert Oracle is a **Knowledge Immortalization Agent** a multi-agent AI system that conducts structured expert interviews, extracts and structures the tacit reasoning behind decisions, and builds a queryable **Expert Twin** that answers in the expert's own voice.

Unlike traditional knowledge management tools that capture *what* was decided, Expert Oracle captures *why* - the conditional logic, the situational triggers, the confidence levels, and the past episodes that informed every judgment.

| Stage | Agent | What It Does |
|-------|-------|-------------|
|  **Ingest** | `WebIngestor` | Reads URLs - Wikipedia, news articles, Forbes profiles - and pre-loads domain knowledge before the interview |
|  **Ingest** | `DocIngestor` | Parses PDF, DOCX, TXT, CSV documents into structured knowledge nuggets |
|  **Ingest** | `YouTubeIngestor` | Fetches video transcripts from talks, interviews, and keynotes |
|  **Interview** | `InterviewerAgent` | Conducts a Socratic interview that probes not just answers, but the *reasoning* behind them |
|  **Extract** | `KnowledgeExtractor` | Decomposes every response into `IF → THEN → BECAUSE` decision logic with confidence levels |
|  **Validate** | `ConflictDetector` | Scans the knowledge base for semantic contradictions, flags tensions by severity, and suggests resolutions |
|  **Respond** | `ExpertTwin` | Answers queries in the expert's voice, citing past situations and stored decision rules |
|  **Explain** | `ExplainerAgent` | Layers every recommendation with a *why* - the causal reasoning behind the advice |
|  **Reason** | `CounterfactualAgent` | Explores the alternative timeline: *"What would have happened if we hadn't followed this advice?"* |

---

##  Live Demo

**Try the deployed application:**  
 [https://expert-oracle-aerubfuwm454utwxysfcvd.streamlit.app/](https://expert-oracle-aerubfuwm454utwxysfcvd.streamlit.app/)

**Watch the full video walkthrough:**  
 [https://youtu.be/TVtIvns8BFU](https://youtu.be/TVtIvns8BFU)

To get started with the demo, use the built-in **"Load Margaret Chen demo scenario"** button on the setup page. This pre-populates a senior financial analyst persona so you can experience the full pipeline immediately without needing to conduct your own interview.

---

##  System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EXPERT ORACLE v2.4                       │
│              Knowledge Immortalization System               │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  INGESTION LAYER (Pre-Interview)            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  WebIngestor │  │  DocIngestor │  │ YouTubeIngestor  │  │
│  │  URLs/Pages  │  │ PDF/DOCX/TXT │  │  Transcripts     │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
└─────────┼─────────────────┼──────────────────-┼────────────┘
          │                 │                   │
          └─────────────────┼───────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   INTERVIEW LAYER                           │
│              InterviewerAgent (Socratic probe)              │
│                         │                                   │
│                         ▼                                   │
│              KnowledgeExtractor                             │
│         (IF → THEN → BECAUSE decomposition)                 │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  MEMORY LAYER                               │
│            ChromaDB Vector Knowledge Store                  │
│    ┌───────────────────────────────────────────────┐        │
│    │  Knowledge Nuggets  │  Tone Profile  │  Metadata │      │
│    └───────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ ConflictDet. │  │  ExpertTwin  │  │  Explainer   │
│  Validation  │  │ Voice+Memory │  │  Why Layer   │
└──────────────┘  └──────┬───────┘  └──────────────┘
                         │
                         ▼
               ┌──────────────────┐
               │ CounterfactualAg │
               │ Alternative Path │
               └──────────────────┘
```

---

##  Agent Pipeline

### 1. Knowledge Ingestion (Pre-Interview)

Three specialised ingestors allow the system to **bootstrap expertise before the interview begins**, meaning the interviewer can probe deeper rather than starting from scratch.

- **`WebIngestor`** -Accepts public URLs and extracts expertise-relevant content using the LLM. Supports Wikipedia, news articles, academic profiles, company bios, and more.
- **`DocIngestor`** - Parses uploaded PDF, DOCX, TXT, and CSV files. Ideal for board reports, published papers, internal memos, and CVs.
- **`YouTubeIngestor`** - Fetches YouTube video transcripts via the YouTube Data API and extracts structured knowledge from talks, interviews, and keynotes.

### 2. Structured Interview

The `InterviewerAgent` conducts a **Socratic knowledge-extraction interview** designed to surface not just decisions, but the conditional logic that produced them. Questions probe:
- *What would trigger this decision?*
- *What have you seen go wrong when this rule was ignored?*
- *How confident are you, and why?*

### 3. Decision Logic Extraction

The `KnowledgeExtractor` decomposes every interview answer into structured **knowledge nuggets** using the `IF → THEN → BECAUSE` format:

```
IF   [condition / trigger]
THEN [recommended action]
BECAUSE [the causal reasoning, grounded in past experience]
```

Each nugget is tagged with:
- **Type**: `decision_rule`, `mental_model`, `heuristic`, `lesson_learned`, `process`, `warning`
- **Confidence level**: `high`, `medium`, `low`
- **Past situations**: episodic memories that ground the rule
- **Source**: interview question, URL, document, or YouTube video

### 4. Knowledge Conflict Detection *(Feature 4)*

The `ConflictDetector` performs pairwise semantic analysis across the entire knowledge base to identify **contradictions**- cases where the expert stated incompatible things across different sessions or sources. Each conflict is:

- Classified by **severity** (`high`, `medium`, `low`)
- Explained with a natural-language summary of the tension
- Resolved with a suggested reconciliation that the Expert Twin can use

### 5. Expert Twin

The `ExpertTwin` is the queryable persona - a retrieval-augmented agent that:
- Retrieves semantically relevant knowledge nuggets from ChromaDB
- Synthesises responses in the expert's **voice profile** (tone markers extracted from the interview transcript)
- Cites the specific past situations and decision rules it is drawing on
- Acknowledges known conflicts in its knowledge base when relevant

### 6. Explanation and Counterfactual Reasoning

- **`ExplainerAgent`** layers every recommendation with the causal *why*, making the reasoning transparent and auditable.
- **`CounterfactualAgent`** reasons through the alternative timeline: *"What would have happened if we had NOT followed this advice?"* - demonstrating the stakes of expert judgment.

---

##  Key Features

- **Multi-source ingestion**- URLs, documents, and YouTube transcripts all feed into a unified knowledge base before the interview even starts
- **Structured decision logic** - the `IF/THEN/BECAUSE` format preserves reasoning, not just conclusions
- **Voice profile replication** - tone markers built from the interview transcript ensure the twin sounds like the expert, not a generic chatbot
- **Layered explanation** - every recommendation comes with a *because*, grounded in episodic memory
- **Counterfactual engine** - demonstrates the value of expert judgment by reasoning through the alternative path
- **Conflict detection** - identifies when the expert's knowledge has evolved or contains internal tensions, enabling honest, nuanced responses
- **Episodic memory** - past situations are vector-indexed and retrieved as evidence for future recommendations
- **Fully deployable** -runs on Streamlit Cloud with zero infrastructure cost using entirely free-tier tools

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **LLM** | Groq API - `llama-3.3-70b-versatile` + `llama-3.1-8b-instant` | Primary reasoning and generation (free tier) |
| **Vector Database** | ChromaDB | Local persistent knowledge store with semantic search |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) | Semantic similarity — runs locally, zero cost |
| **Orchestration** | LangChain | Agent and chain management |
| **UI** | Streamlit | Interactive web interface |
| **Document Parsing** | PyMuPDF, python-docx, pandas | PDF, DOCX, TXT, CSV ingestion |
| **YouTube Transcripts** | `youtube-transcript-api` | Video caption extraction |
| **Environment** | python-dotenv | Secure API key management |

**Total infrastructure cost: $0** - the entire stack operates on free tiers and local computation.

---

##  Project Structure

```
expert-oracle/
│
├── app.py                    # Main Streamlit application (1,126 lines)
├── requirements.txt          # Python dependencies
├── .gitignore
│
├── agents/                   # Multi-agent system
│   ├── interviewer.py        # Socratic interview conductor
│   ├── extractor.py          # IF/THEN/BECAUSE knowledge extractor + tone profiler
│   ├── twin.py               # Expert Twin — retrieval-augmented persona
│   ├── explainer.py          # Causal explanation layer
│   ├── counterfactual.py     # Alternative timeline reasoning
│   ├── web_ingestor.py       # URL ingestion agent
│   ├── doc_ingestor.py       # Document ingestion agent (PDF, DOCX, TXT, CSV)
│   ├── youtube_ingestor.py   # YouTube transcript ingestion agent
│   └── conflict_detector.py  # Semantic contradiction detector
│
├── memory/
│   └── store.py              # ChromaDB knowledge store interface
│
├── Documents/                # Supporting documentation
│
└── .streamlit/               # Streamlit Cloud configuration
```

---

##  Getting Started

### Prerequisites

- Python 3.10+
- A free Groq API key - obtain one at [console.groq.com](https://console.groq.com)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/ThesanyaLamahewa/expert-oracle.git
cd expert-oracle

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
echo GROQ_API_KEY=your_key_here > .env

# 5. Launch the application
streamlit run app.py
```

The application will open at `http://localhost:8501`.

### Streamlit Cloud Deployment

To deploy on Streamlit Cloud:

1. Fork this repository
2. Connect it to your Streamlit Cloud account
3. Add `GROQ_API_KEY` under **App Settings → Secrets**
4. Deploy - no additional configuration required

---

##  Usage Guide

### Setting Up an Expert Session

1. Enter the **expert's name** and **domain of expertise**
2. Optionally provide pre-interview context via:
   - **URLs** - paste public web links (one per line)
   - **Documents** - upload PDF, DOCX, TXT, or CSV files
   - **YouTube links** - paste video URLs (one per line)
3. Click **Begin knowledge capture**

### Conducting the Interview

- Answer the AI interviewer's questions **as the expert** - the more specific and experiential your answers, the richer the knowledge base
- Watch the **Live Extraction** panel on the right to see decision logic captured in real time
- Aim for at least **25 knowledge nuggets** before building the twin (minimum: 5)

### Consulting the Expert Twin

Once the twin is built, switch to the **Expert Twin** tab to ask any question. The twin will:
- Answer in the expert's voice using stored decision rules
- Cite specific past situations and reasoning patterns
- Offer counterfactual analysis on request

### Running Conflict Detection

Navigate to **Knowledge Archive → Conflict Detection** and click **Scan for conflicts**. The system analyses every nugget pair and returns a severity-ranked list of contradictions, each with a suggested resolution.

---
| **System Version** | v2.4 - Four core features implemented |

### Feature Summary (v2.4)

| Feature | Status | Description |
|---------|--------|-------------|
| Feature 1: URL Intelligence Ingestion |  Complete | Web-based knowledge pre-loading |
| Feature 2: Document Intelligence Ingestion |  Complete | Multi-format document parsing |
| Feature 3: YouTube Intelligence Ingestion |  Complete | Video transcript extraction |
| Feature 4: Knowledge Conflict Detector |  Complete | Semantic contradiction analysis |

---

##  Acknowledgements

- [Groq](https://groq.com) for ultra-fast LLM inference on the free tier
- [ChromaDB](https://www.trychroma.com) for the open-source vector database
- [Streamlit](https://streamlit.io) for the deployment platform
- [LangChain](https://www.langchain.com) for agent orchestration primitives
- [Hugging Face](https://huggingface.co) for the `sentence-transformers` library

---

<div align="center">

**Expert Oracle** 

[![Live App](https://img.shields.io/badge/Try_It_Live-Click_Here-FF4B4B?style=for-the-badge)](https://expert-oracle-aerubfuwm454utwxysfcvd.streamlit.app/)
[![Watch Demo](https://img.shields.io/badge/Watch_Demo-YouTube-FF0000?style=for-the-badge&logo=youtube)](https://youtu.be/TVtIvns8BFU)

*Real pain addressed: an estimated $4.1 trillion in institutional knowledge is lost annually to workforce transitions.*

</div>
