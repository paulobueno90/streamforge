from typing import Dict


def transform(record: dict, map_obj: Dict[str, str]) -> dict:
    if map_obj is None:
        return record
    else:
        return {
            out_key: record[in_key]
            for in_key, out_key in map_obj.items()
        }