# storage/json_storage.py

import json
from pathlib import Path


def save_json(data, filepath):

    Path(filepath).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )