import json

from config import CLEAN_FILE, FINAL_FILE



with open(
    CLEAN_FILE,
    encoding="utf-8"
) as f:

    data=json.load(f)



seen=set()

final=[]



for article in data:


    key = (

        article["source"]

        if article["source"]

        else article["title"]

    )



    if key in seen:

        continue



    seen.add(key)

    final.append(article)



with open(
    FINAL_FILE,
    "w",
    encoding="utf-8"
) as f:


    json.dump(
        final,
        f,
        ensure_ascii=False,
        indent=2
    )



print(
    "After duplicate removal:",
    len(final)
)