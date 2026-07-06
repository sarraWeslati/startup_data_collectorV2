import json
import re

def safe_json(text):

    if not text:
        return None

    try:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return None

        return json.loads(match.group(0))

    except:
        return None