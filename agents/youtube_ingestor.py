"""
agents/youtube_ingestor.py
--------------------------
YouTube Intelligence Ingestion Agent — Feature 3
Compatible with youtube-transcript-api 0.6.1
"""

import os
import json
import re
from groq import Groq

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
    )
    YT_AVAILABLE = True
except ImportError:
    YT_AVAILABLE = False


class YouTubeIngestor:

    def __init__(self):
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model  = "llama-3.1-8b-instant"

    def ingest(self, youtube_urls: list, expert_name: str, domain: str) -> dict:
        if not YT_AVAILABLE:
            return {
                "nuggets":  [],
                "sources":  [],
                "warnings": ["youtube-transcript-api not installed. Run: pip install youtube-transcript-api==0.6.1"],
                "total":    0,
            }

        all_nuggets = []
        sources     = []
        warnings    = []

        for raw_url in youtube_urls:
            url = raw_url.strip()
            if not url:
                continue

            video_id, id_error = self._extract_video_id(url)
            if id_error:
                warnings.append(f"⚠️  {url} — {id_error}")
                continue

            transcript_text, fetch_error = self._fetch_transcript(video_id)
            if fetch_error:
                warnings.append(f"⚠️  {url} — {fetch_error}")
                continue

            if len(transcript_text.strip()) < 100:
                warnings.append(f"⚠️  {url} — Transcript too short.")
                continue

            nuggets = self._extract_from_transcript(
                transcript=transcript_text,
                video_id=video_id,
                expert_name=expert_name,
                domain=domain,
            )

            if nuggets:
                all_nuggets.extend(nuggets)
                sources.append(f"youtube.com/watch?v={video_id}")
            else:
                warnings.append(f"⚠️  {url} — No expertise signals found in transcript.")

        return {
            "nuggets":  all_nuggets,
            "sources":  sources,
            "warnings": warnings,
            "total":    len(all_nuggets),
        }

    def _extract_video_id(self, url: str) -> tuple:
        patterns = [
            r"(?:v=)([a-zA-Z0-9_-]{11})",
            r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
            r"(?:embed/)([a-zA-Z0-9_-]{11})",
            r"(?:shorts/)([a-zA-Z0-9_-]{11})",
        ]
        for pattern in patterns:
            m = re.search(pattern, url)
            if m:
                return m.group(1), None
        stripped = url.strip().replace("https://","").replace("http://","")
        if re.match(r"^[a-zA-Z0-9_-]{11}$", stripped):
            return stripped, None
        return None, "Could not extract a valid YouTube video ID."

    def _fetch_transcript(self, video_id: str) -> tuple:
        """
        Returns (transcript_text, error_string).
        error_string is None on success.
        """
        try:
            # Approach 1: get_transcript class method (0.6.x standard)
            try:
                entries = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=["en", "en-US", "en-GB"]
                )
                return self._clean_transcript(entries), None
            except Exception:
                pass

            # Approach 2: list_transcripts (older API)
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                try:
                    t = transcript_list.find_manually_created_transcript(["en"])
                except Exception:
                    try:
                        t = transcript_list.find_generated_transcript(["en"])
                    except Exception:
                        t = next(iter(transcript_list))
                entries = t.fetch()
                return self._clean_transcript(entries), None
            except Exception:
                pass

            # Approach 3: bare get_transcript with no language preference
            try:
                entries = YouTubeTranscriptApi.get_transcript(video_id)
                return self._clean_transcript(entries), None
            except Exception:
                pass

            return "", "Could not fetch transcript. Video may have captions disabled."

        except Exception as e:
            err = str(e).lower()
            if "disabled" in err:
                return "", "Transcripts are disabled for this video."
            if "unavailable" in err or "private" in err:
                return "", "Video is unavailable or private."
            if "429" in err or "too many" in err:
                return "", "YouTube rate limit. Wait 1 minute and try again."
            return "", f"Error: {str(e)[:100]}"

    def _clean_transcript(self, entries: list) -> str:
        """Join entries, remove artifacts, cap length."""
        text = " ".join(e.get("text", "") for e in entries)
        text = re.sub(r"\[.*?\]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:4500]

    def _extract_from_transcript(
        self,
        transcript: str,
        video_id: str,
        expert_name: str,
        domain: str,
    ) -> list:
        source = f"youtube.com/watch?v={video_id}"

        prompt = f"""You are a knowledge engineering specialist analysing a YouTube transcript.

EXPERT NAME: {expert_name}
DOMAIN: {domain}
SOURCE: {source}

TRANSCRIPT:
{transcript}

Extract 3 to 6 knowledge nuggets revealing decision frameworks,
stated opinions, lessons from experience, mental models, or warnings.

Each nugget MUST have ALL fields:
"content"         : Standalone knowledge statement (first person if speaker is expert)
"type"            : decision_rule / mental_model / heuristic / lesson_learned / process / warning
"decision_logic"  : "IF [trigger] THEN [action] BECAUSE [domain-specific reasoning]"
"past_situations" : JSON array of examples mentioned. [] if none.
"confidence_level": high / medium / low
"tone_marker"     : emphatic / analytical / cautious / decisive / reflective
"source"          : "youtube: {source}"

Return ONLY valid JSON array. No markdown. No preamble. If nothing found return []"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1800,
            )
            raw = resp.choices[0].message.content.strip()
            if "```" in raw:
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else raw
                if raw.lower().startswith("json"):
                    raw = raw[4:]
            nuggets = json.loads(raw.strip())
            if isinstance(nuggets, list):
                for n in nuggets:
                    if "source" not in n:
                        n["source"] = f"youtube: {source}"
                return nuggets
        except Exception:
            pass
        return []