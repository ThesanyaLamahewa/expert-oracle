import os
import json
import requests
from groq import Groq
from bs4 import BeautifulSoup

BLOCKED_DOMAINS = ["linkedin.com", "facebook.com", "instagram.com", "twitter.com", "x.com"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


class WebIngestor:

    def __init__(self):
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model  = "llama-3.1-8b-instant"

    def ingest(self, urls: list, expert_name: str, domain: str) -> dict:
        all_nuggets = []
        sources     = []
        warnings    = []

        for raw_url in urls:
            url = raw_url.strip()
            if not url:
                continue
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            if any(blocked in url for blocked in BLOCKED_DOMAINS):
                warnings.append(
                    f"⚠️  {url} — This site blocks automated access. "
                    f"Copy and paste the text manually instead."
                )
                continue
            text, error = self._fetch_and_clean(url)
            if error:
                warnings.append(f"⚠️  {url} — {error}")
                continue
            if len(text) < 150:
                warnings.append(f"⚠️  {url} — Page appears empty or requires login.")
                continue
            nuggets = self._extract_from_text(
                text=text,
                source_url=url,
                expert_name=expert_name,
                domain=domain,
            )
            if nuggets:
                all_nuggets.extend(nuggets)
                sources.append(url)

        return {
            "nuggets":  all_nuggets,
            "sources":  sources,
            "warnings": warnings,
            "total":    len(all_nuggets),
        }

    def _fetch_and_clean(self, url: str) -> tuple:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=12)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header",
                              "aside", "form", "button", "iframe", "noscript"]):
                tag.decompose()
            main_content = (
                soup.find("article") or
                soup.find("main") or
                soup.find("body")
            )
            text = main_content.get_text(separator="\n", strip=True) if main_content else ""
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text  = "\n".join(lines)
            return text[:4000], None
        except requests.exceptions.Timeout:
            return "", "Connection timed out."
        except requests.exceptions.HTTPError as e:
            return "", f"HTTP {e.response.status_code} — Page not accessible."
        except requests.exceptions.ConnectionError:
            return "", "Could not connect. Check the URL."
        except Exception as e:
            return "", f"Error: {str(e)[:100]}"

    def _extract_from_text(
        self,
        text: str,
        source_url: str,
        expert_name: str,
        domain: str,
    ) -> list:
        prompt = f"""You are a knowledge engineering specialist analysing public content about a domain expert.

EXPERT NAME: {expert_name}
DOMAIN: {domain}
SOURCE: {source_url}

CONTENT:
{text}

Extract 3 to 6 knowledge nuggets revealing this person's decision-making philosophy,
stated opinions, professional principles, lessons from experience, or mental models.

Return a JSON array. Each item MUST have ALL these fields:
"content"         : Clear standalone statement. Write in third person.
"type"            : One of: decision_rule / mental_model / heuristic / lesson_learned / process / warning
"decision_logic"  : "IF [trigger] THEN [action] BECAUSE [their reasoning]"
"past_situations" : JSON array of specific situations mentioned. [] if none.
"confidence_level": "high" / "medium" / "low"
"tone_marker"     : Single word e.g. emphatic / analytical / cautious
"source"          : "{source_url}"

Return ONLY valid JSON array. No markdown. No preamble. If nothing useful found return []"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1500,
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
                        n["source"] = source_url
                return nuggets
        except Exception:
            pass
        return []