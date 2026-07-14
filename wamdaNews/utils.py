import json
from pathlib import Path



def save_json(data):

    Path(
        "storage"
    ).mkdir(
        exist_ok=True
    )


    with open(
        "storage/wamda_news.json",
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )