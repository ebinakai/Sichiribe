import logging
import json
import csv
from itertools import zip_longest
from typing import List, Dict, Any, Union
from pathlib import Path

logger = logging.getLogger("__main__").getChild(__name__)


def get_supported_formats() -> List[str]:
    return ["csv", "json"]


def export(
    data: Union[List, Dict], format: str, out_dir: Union[str, Path], prefix: str
) -> None:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    if format == "csv":
        if isinstance(data, dict):
            data = [data]
        to_csv(data, out_dir, prefix)
    elif format == "json":
        to_json(data, out_dir, prefix)
    elif format == "dummy":
        return
    else:
        raise ValueError("Invalid export method.")


def to_json(data: Union[Dict, List], out_dir, prefix: str) -> None:
    out_path = Path(out_dir) / f"{prefix}.json"
    with open(out_path, "w") as f:
        json.dump(data, f)
    logger.debug("Exported data to json.")


def to_csv(data: List[Dict], out_dir, prefix: str) -> None:
    out_path = Path(out_dir) / f"{prefix}.csv"
    keys = data[0].keys()
    with open(out_path, "w", newline="") as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    logger.debug("Exported data to csv.")


def build_data_records(data_dict: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    records = []
    field_names = list(data_dict.keys())
    data_lists = list(data_dict.values())

    for values in zip_longest(*data_lists):
        record = {field: value for field, value in zip(field_names, values)}
        records.append(record)

    return records
