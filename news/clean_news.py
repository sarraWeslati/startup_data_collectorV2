import json
import re

from config import NORMALIZED_FILE, CLEAN_FILE



def clean_text(text):

    if not text:
        return ""


    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )


    text = re.sub(
        r"\s+",
        " ",
        text
    )


    text=text.strip()


    return text




with open(
    NORMALIZED_FILE,
    encoding="utf-8"
) as f:

    data=json.load(f)




cleaned=[]


for item in data:


    item["title"] = clean_text(
        item["title"]
    )


    item["summary"] = clean_text(
        item["summary"]
    )


    item["content"] = clean_text(
        item["content"]
    )



    if not item["content"]:

        continue


    cleaned.append(item)




with open(
    CLEAN_FILE,
    "w",
    encoding="utf-8"
) as f:


    json.dump(
        cleaned,
        f,
        ensure_ascii=False,
        indent=2
    )



print(
    "Clean articles:",
    len(cleaned)
)