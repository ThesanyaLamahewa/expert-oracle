"""
agents/doc_ingestor.py
----------------------
Document Intelligence Ingestion Agent — Feature 2

Supports: PDF, Word (.docx), plain text (.txt), CSV (.csv)

Accepts Streamlit uploaded file objects directly.
Extracts text from each file type, then uses Groq to pull out
IF/THEN/BECAUSE knowledge nuggets in the same format as
web_ingestor.py and extractor.py.

No changes needed to any other agent or store.py.
"""

import os
import json
import io
import csv

from groq import Groq

# PDF extraction
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Word document extraction
try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# CSV / pandas
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class DocIngestor:
    """
    Reads uploaded files, extracts clean text, and uses Groq to
    pull out structured knowledge nuggets in IF/THEN/BECAUSE format.
    """

    def __init__(self):
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model  = "llama-3.1-8b-instant"

    # ──────────────────────────────────────────
    # PUBLIC METHOD
    # ──────────────────────────────────────────

    def ingest(
        self,
        uploaded_files: list,
        expert_name: str,
        domain: str,
    ) -> dict:
        """
        Process a list of Streamlit UploadedFile objects.

        Returns:
        {
            "nuggets":  [ list of nugget dicts ],
            "sources":  [ list of filenames successfully processed ],
            "warnings": [ list of warning strings ],
            "total":    int
        }
        """
        all_nuggets = []
        sources     = []
        warnings    = []

        for uploaded_file in uploaded_files:
            filename  = uploaded_file.name
            extension = filename.rsplit(".", 1)[-1].lower()

            # Extract raw text based on file type
            text, error = self._extract_text(uploaded_file, extension, filename)

            if error:
                warnings.append(f"⚠️  {filename} — {error}")
                continue

            if not text or len(text.strip()) < 100:
                warnings.append(f"⚠️  {filename} — File appears empty or unreadable.")
                continue

            # Extract knowledge nuggets from the text
            nuggets = self._extract_from_text(
                text=text,
                filename=filename,
                expert_name=expert_name,
                domain=domain,
            )

            if nuggets:
                all_nuggets.extend(nuggets)
                sources.append(filename)
            else:
                warnings.append(
                    f"⚠️  {filename} — Processed but no clear expertise signals found."
                )

        return {
            "nuggets":  all_nuggets,
            "sources":  sources,
            "warnings": warnings,
            "total":    len(all_nuggets),
        }

    # ──────────────────────────────────────────
    # TEXT EXTRACTION PER FILE TYPE
    # ──────────────────────────────────────────

    def _extract_text(self, uploaded_file, extension: str, filename: str) -> tuple:
        """
        Dispatch to the correct extractor based on file extension.
        Returns (text, error_string). error_string is None on success.
        """
        try:
            if extension == "pdf":
                return self._extract_pdf(uploaded_file)
            elif extension == "docx":
                return self._extract_docx(uploaded_file)
            elif extension == "txt":
                return self._extract_txt(uploaded_file)
            elif extension == "csv":
                return self._extract_csv(uploaded_file)
            else:
                return "", f"Unsupported file type .{extension}"
        except Exception as e:
            return "", f"Unexpected error reading file: {str(e)[:120]}"

    def _extract_pdf(self, uploaded_file) -> tuple:
        if not PDF_AVAILABLE:
            return "", "pdfplumber not installed. Run: pip install pdfplumber"
        try:
            # Read bytes from Streamlit UploadedFile
            file_bytes = uploaded_file.read()
            pages_text = []
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages[:20]:  # cap at 20 pages
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append(page_text.strip())
            text = "\n\n".join(pages_text)
            return text[:5000], None
        except Exception as e:
            return "", f"Could not read PDF: {str(e)[:100]}"

    def _extract_docx(self, uploaded_file) -> tuple:
        if not DOCX_AVAILABLE:
            return "", "python-docx not installed. Run: pip install python-docx"
        try:
            file_bytes = uploaded_file.read()
            doc = DocxDocument(io.BytesIO(file_bytes))
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            text = "\n\n".join(paragraphs)
            return text[:5000], None
        except Exception as e:
            return "", f"Could not read Word document: {str(e)[:100]}"

    def _extract_txt(self, uploaded_file) -> tuple:
        try:
            # Try UTF-8 first, fall back to latin-1
            raw = uploaded_file.read()
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("latin-1")
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            return "\n".join(lines)[:5000], None
        except Exception as e:
            return "", f"Could not read text file: {str(e)[:100]}"

    def _extract_csv(self, uploaded_file) -> tuple:
        try:
            raw = uploaded_file.read()
            try:
                text_data = raw.decode("utf-8")
            except UnicodeDecodeError:
                text_data = raw.decode("latin-1")

            if PANDAS_AVAILABLE:
                # Use pandas for smart CSV reading
                df = pd.read_csv(io.StringIO(text_data))
                # Convert each row to a readable sentence
                rows_as_text = []
                for _, row in df.head(50).iterrows():  # cap at 50 rows
                    row_text = " | ".join(
                        f"{col}: {val}"
                        for col, val in row.items()
                        if pd.notna(val) and str(val).strip()
                    )
                    if row_text:
                        rows_as_text.append(row_text)
                text = f"CSV with {len(df)} rows and columns: {', '.join(df.columns)}\n\n"
                text += "\n".join(rows_as_text)
            else:
                # Fallback: plain csv reader
                reader = csv.reader(io.StringIO(text_data))
                rows_as_text = [", ".join(row) for row in reader]
                text = "\n".join(rows_as_text)

            return text[:5000], None
        except Exception as e:
            return "", f"Could not read CSV: {str(e)[:100]}"

    # ──────────────────────────────────────────
    # KNOWLEDGE EXTRACTION VIA GROQ
    # ──────────────────────────────────────────

    def _extract_from_text(
        self,
        text: str,
        filename: str,
        expert_name: str,
        domain: str,
    ) -> list:
        """
        Use Groq to extract IF/THEN/BECAUSE knowledge nuggets
        from the document text.
        """

        prompt = f"""You are a knowledge engineering specialist analysing a document related to a domain expert.

EXPERT NAME: {expert_name}
DOMAIN: {domain}
SOURCE DOCUMENT: {filename}

DOCUMENT CONTENT:
{text}

Your task: Extract 3 to 8 knowledge nuggets that reveal this expert's or document's:
- Decision-making frameworks or rules
- Stated opinions, positions, or recommendations
- Professional principles or standards they follow
- Lessons from past experience or case studies
- Mental models used to analyse problems
- Warnings about common mistakes or risks

For each nugget return a JSON object with ALL these fields:

"content"         : Clear standalone knowledge statement written in a way that
                    captures the core insight. If the document is written by or
                    about the expert write in third person: "{expert_name} believes..."
                    If it is a general document, write the insight directly.
"type"            : Exactly one of: decision_rule / mental_model / heuristic /
                    lesson_learned / process / warning
"decision_logic"  : "IF [specific trigger or situation] THEN [specific action or stance]
                    BECAUSE [the reasoning — make this domain-specific and concrete]"
"past_situations" : JSON array of specific examples, case studies, or situations
                    mentioned in the document. [] if none.
"confidence_level": "high" if stated emphatically, "medium" if measured, "low" if implied
"tone_marker"     : Single word: emphatic / analytical / cautious / decisive /
                    reflective / urgent / matter-of-fact
"source"          : "document: {filename}"

Return ONLY a valid JSON array. No markdown fences. No explanation. No preamble.
If no meaningful expertise can be extracted return empty array: []"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2000,
            )
            raw = resp.choices[0].message.content.strip()

            # Strip markdown code fences if model added them
            if "```" in raw:
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else raw
                if raw.lower().startswith("json"):
                    raw = raw[4:]

            nuggets = json.loads(raw.strip())
            if isinstance(nuggets, list):
                # Tag each nugget with its source document
                for n in nuggets:
                    if "source" not in n:
                        n["source"] = f"document: {filename}"
                return nuggets

        except Exception:
            pass

        return []