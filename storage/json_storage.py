# storage/json_storage.py

import json
from pathlib import Path
from copy import deepcopy
from pathlib import Path

def merge_json(
    old,
    new
):
    """
    Fusion récursive de deux JSON.
    """

    if isinstance(old, dict) and isinstance(new, dict):

        merged = deepcopy(old)

        for key, value in new.items():

            if value in (
                "",
                None,
                [],
                {}
            ):
                continue

            if key not in merged:

                merged[key] = value

            else:

                merged[key] = merge_json(
                    merged[key],
                    value
                )

        return merged

    if isinstance(old, list) and isinstance(new, list):

        merged = old.copy()

        for item in new:

            if item not in merged:

                merged.append(item)

        return merged

    return old if old not in (
        "",
        None,
        [],
        {}
    ) else new

def save_json(
    data,
    filepath
):

    filepath = Path(filepath)

    filepath.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if filepath.exists():

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as f:

                old_data = json.load(f)

        except Exception:

            old_data = {}

        data = merge_json(
            old_data,
            data
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

    return filepath