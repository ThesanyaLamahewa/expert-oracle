"""
memory/store.py
---------------
The persistent memory brain of the Expert Twin system.

v2 — Uses ChromaDB's built-in DefaultEmbeddingFunction (onnxruntime-based)
     instead of sentence_transformers. This avoids the PyTorch/torch
     dependency that Windows Application Control policies block.
"""

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import uuid
import json
from datetime import datetime


class KnowledgeStore:

    def __init__(self, expert_name: str):
        self.expert_name = expert_name

        # PersistentClient saves to disk — survives app restarts
        self.client = chromadb.PersistentClient(path="./data/chroma_db")

        # DefaultEmbeddingFunction uses onnxruntime — no PyTorch needed
        # Downloads a small ONNX model (~30MB) once, then runs locally forever
        self.embedder = DefaultEmbeddingFunction()

        # Sanitise name for use as collection ID
        safe = (
            expert_name.lower()
            .replace(" ", "_")
            .replace(".", "")
            .replace("-", "_")
        )

        # Pass the embedding function directly to the collection
        # so ChromaDB handles embeddings automatically
        self.col = self.client.get_or_create_collection(
            name=safe + "_v3_knowledge",
            embedding_function=self.embedder,
            metadata={"hnsw:space": "cosine"},
        )
        self.tone_col = self.client.get_or_create_collection(
            name=safe + "_v3_tone",
            embedding_function=self.embedder,
            metadata={"hnsw:space": "cosine"},
        )

    # ──────────────────────────────────────────
    # KNOWLEDGE OPERATIONS
    # ──────────────────────────────────────────

    def add_knowledge(
        self,
        content: str,
        knowledge_type: str,
        source_question: str = "",
        decision_logic: str = "",
        past_situations: list = None,
        confidence_level: str = "medium",
    ):
        """Store one structured knowledge nugget."""
        # No manual embedding — ChromaDB handles it automatically
        self.col.add(
            ids=[str(uuid.uuid4())],
            documents=[content],
            metadatas=[{
                "type":             knowledge_type,
                "source_question":  source_question[:200],
                "expert":           self.expert_name,
                "timestamp":        datetime.now().isoformat(),
                "decision_logic":   (decision_logic or "")[:600],
                "past_situations":  json.dumps(past_situations or []),
                "confidence_level": confidence_level,
            }],
        )

    def retrieve_relevant(self, query: str, n: int = 6) -> dict:
        """Semantic search — find the most relevant nuggets for a query."""
        count = self.col.count()
        if count == 0:
            return {"documents": [[]], "metadatas": [[]]}
        return self.col.query(
            query_texts=[query],
            n_results=min(n, count),
        )

    def get_all(self) -> dict:
        return self.col.get()

    def count(self) -> int:
        return self.col.count()

    # ──────────────────────────────────────────
    # TONE PROFILE OPERATIONS
    # ──────────────────────────────────────────

    def save_tone_profile(self, profile: dict):
        """Upsert the expert's voice profile (update if exists)."""
        text = (
            f"Style: {profile.get('communication_style', '')}. "
            f"Tone: {', '.join(profile.get('tone_markers', []))}."
        )
        self.tone_col.upsert(
            ids=["tone_profile"],
            documents=[text],
            metadatas=[{
                "communication_style": profile.get("communication_style", "")[:400],
                "tone_markers":        json.dumps(profile.get("tone_markers", [])),
                "vocabulary_style":    profile.get("vocabulary_style", "balanced"),
                "signature_phrases":   json.dumps(profile.get("signature_phrases", [])),
                "updated":             datetime.now().isoformat(),
            }],
        )

    def get_tone_profile(self) -> dict:
        """Return the stored tone profile, or safe defaults."""
        try:
            result = self.tone_col.get(ids=["tone_profile"])
            if result and result["metadatas"]:
                m = result["metadatas"][0]
                return {
                    "communication_style": m.get("communication_style", ""),
                    "tone_markers":        json.loads(m.get("tone_markers", "[]")),
                    "vocabulary_style":    m.get("vocabulary_style", "balanced"),
                    "signature_phrases":   json.loads(m.get("signature_phrases", "[]")),
                }
        except Exception:
            pass
        return {
            "communication_style": "Direct, experienced, and confident.",
            "tone_markers":        ["authoritative", "direct", "analytical"],
            "vocabulary_style":    "balanced",
            "signature_phrases":   [],
        }