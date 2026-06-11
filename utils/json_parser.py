import json
import re
from typing import Optional
from utils.logger import logger

def safe_parse_json(raw: str) -> Optional[dict]:
    """
    Safely parse a JSON string from a Groq response.
    Handles common issues: markdown fences, leading text, trailing text.
    """
    if not raw:
        return None

    # Strip markdown code fences if present
    raw = re.sub(r"```json\s*", "", raw)
    raw = re.sub(r"```\s*", "", raw)
    raw = raw.strip()

    # Try direct parse
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed[0] if len(parsed) > 0 and isinstance(parsed[0], dict) else {}
        if isinstance(parsed, dict):
            return parsed
        return {}
    except json.JSONDecodeError:
        pass

    # Try extracting first JSON object
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extracted JSON object: {e}")
            pass

    logger.error("Failed to parse JSON from response entirely.")
    return None
