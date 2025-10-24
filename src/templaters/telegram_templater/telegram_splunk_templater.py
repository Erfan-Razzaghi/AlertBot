import logging
import urllib.parse

logger = logging.getLogger(__name__) 

class TelegramSplunkTemplater:
    def __init__(self, keys: list, request_body: dict):
        self.keys = keys
        self.request_body = request_body
        self.message = ""
        self.generate_message()

    def generate_message(self):
        # Implement message generation logic here
        for key in self.keys:
            try:
                self.message += f"<b>{key}: </b>"
                if key == "results_link":
                    self.message += self.get_result_link(
                        self.request_body.get(key)
                    )
                elif key == "result":
                    self.add_result_to_message(self.request_body.get(key))
                else:
                    self.message += f"{self.request_body.get(key, 'this key not found in body!')}"
            except Exception:
                # Log and continue so an error building one field doesn't stop the whole message
                logger.exception("Error while generating message field '%s'", key)
                self.message += "(error building field)"
            finally:
                self.message += "\n"

    def get_result_link(self, raw_link):
        if not raw_link:
            return "No link provided!"

        # Clean up surrounding whitespace or quotes that may come from payload
        raw_link = raw_link.strip().strip('"').strip("'")

        # Some payloads include surrounding angle brackets or trailing commas
        # (e.g. "<http://...>,"). Remove common wrappers that are not part
        # of the URL so parsing/encoding doesn't introduce extra characters.
        if raw_link.startswith("<") and raw_link.endswith(">"):
            raw_link = raw_link[1:-1].strip()
        if raw_link.endswith(","):
            raw_link = raw_link[:-1].strip()

        # Parse the incoming URL and recompose it with the desired host.
        try:
            parsed = urllib.parse.urlparse(raw_link)
        except Exception:
            logger.exception("Failed to parse raw results_link")
            return raw_link

        new_netloc = "fsplunk.company.com"
        scheme = "https"

        # Collapse common double-encoding artifact (%25 -> %) in the query
        query = (parsed.query or "").replace("%25", "%")

        # If the incoming query is a job-based loadjob (e.g. starts with '|loadjob'),
        # try to replace it with the original/full search from the webhook payload
        # so clicking the link shows the intended search query.
        try:
            q_params = urllib.parse.parse_qs(query, keep_blank_values=True)
        except Exception:
            q_params = {}

        incoming_q = None
        if isinstance(q_params, dict):
            incoming_q = q_params.get("q", [None])[0]

        if incoming_q and isinstance(incoming_q, str) and incoming_q.lstrip().startswith("|loadjob"):
            # Look for original search strings in common payload keys
            candidate_keys = [
                "search",
                "saved_search",
                "savedsearch",
                "search_name",
                "saved_search_name",
                "query",
                "raw_search",
                "q",
            ]
            saved_q = None
            for k in candidate_keys:
                v = self.request_body.get(k)
                if v and isinstance(v, str) and v.strip():
                    saved_q = v.strip()
                    break

            if saved_q:
                # Only accept saved_q if it looks like a Splunk query, not just a
                # human-friendly saved-search name. Heuristics: contains 'index=',
                # contains a pipe '|' or contains common Splunk keywords.
                lower = saved_q.lower()
                looks_like_query = (
                    "index=" in lower or
                    "|" in saved_q or
                    any(k in lower for k in ("stats ", "where ", "search ", "eval "))
                )
                if not looks_like_query:
                    saved_q = None

            if saved_q:
                # Ensure saved_q is percent-encoded for use in URL (unless already encoded)
                if "%" in saved_q:
                    encoded_q = saved_q
                else:
                    encoded_q = urllib.parse.quote(saved_q, safe="")

                # preserve earliest/latest if present
                earliest = q_params.get("earliest", [None])[0]
                latest = q_params.get("latest", [None])[0]

                pieces = [f"q={encoded_q}"]
                if earliest:
                    pieces.append(f"earliest={urllib.parse.quote(earliest, safe='')}" )
                if latest:
                    pieces.append(f"latest={urllib.parse.quote(latest, safe='')}" )

                rebuilt_query = "&".join(pieces)

                path = parsed.path or ""
                # prefer '/en-US' prefix when constructing external link into Splunk UI
                if path.startswith("/app/"):
                    path = "/en-US" + path

                rebuilt = urllib.parse.urlunparse((
                    scheme,
                    new_netloc,
                    path,
                    parsed.params or "",
                    rebuilt_query,
                    parsed.fragment or "",
                ))
                rebuilt = rebuilt.strip().strip('"').strip("'")
                return f'<a href="{rebuilt}">results_link</a>'

        # Fallback: Rebuild using https + public netloc and the original path/query/fragment
        rebuilt = urllib.parse.urlunparse((
            scheme,
            new_netloc,
            parsed.path or "",
            parsed.params or "",
            query,
            parsed.fragment or "",
        ))

        # As a final safety step, ensure there are no stray spaces or quotes
        # inside the rebuilt URL which could show up in Telegram and break the link.
        rebuilt = rebuilt.strip().strip('"').strip("'")

        return f'<a href="{rebuilt}">results_link</a>'

    def add_result_to_message(self, result: dict):
        if result is None:
            self.message += "No result in response!"
            return
        self.message += "\n"
        # Prefer concise output: show funcName and count when available.
        try:
            if isinstance(result, dict):
                # Show the first two top-level fields available in the result dict.
                keys = list(result.keys())[:2]
                if not keys:
                    self.message += "   (no fields)\n"
                else:
                    for k in keys:
                        try:
                            self.message += f"   {k}: {result[k]}\n"
                        except Exception:
                            logger.exception("Error formatting result item %s", k)
                            self.message += f"   {k}: (error)\n"
            else:
                # Non-dict result: display minimal textual representation
                self.message += f"   {result}\n"
        except Exception:
            logger.exception("Error formatting result")
            self.message += "   (error formatting result)\n"

    def get_message(self):
        return self.message