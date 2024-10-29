import logging
import json
import csv
import os
from typing import List, Dict
from cores.common import get_now_str
from pathlib import Path


def get_supported_formats() -> List[str]:
    return Exporter.aveilable_formats


class Exporter:
    # インスタンス化しなくてもサポートフォーマットを取得するためにクラス変数として定義
    aveilable_formats = ["csv", "json"]

    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        self.logger = logging.getLogger("__main__").getChild(__name__)
        os.makedirs(out_dir, exist_ok=True)

        self.logger.debug("Exporter loaded.")

    def export(
        self, data: List | Dict, method: str, prefix: str, with_timestamp: bool = True
    ) -> None:
        if method == "csv":
            if isinstance(data, dict):
                data = [data]
            self.to_csv(data, prefix, with_timestamp)
        elif method == "json":
            self.to_json(data, prefix, with_timestamp)
        elif method == "dummy":
            pass
        else:
            self.logger.error("Invalid export method.")

    def generate_filepath(
        self, prefix: str, extension: str, with_timestamp: bool
    ) -> Path:
        if with_timestamp:
            now = get_now_str()
            filename = f"{prefix}_{now}.{extension}"
        else:
            filename = f"{prefix}.{extension}"
        return Path(self.out_dir) / filename

    def to_csv(self, data: List[Dict], prefix: str, with_timestamp: bool) -> None:
        if not data:
            self.logger.debug("No data to export.")
            return
        out_path = self.generate_filepath(prefix, "csv", with_timestamp)
        keys = data[0].keys()
        with open(out_path, "w", newline="") as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        self.logger.debug("Exported data to csv.")

    def to_json(self, data: Dict | List, prefix: str, with_timestamp: bool) -> None:
        if not data:
            self.logger.debug("No data to export.")
            return
        out_path = self.generate_filepath(prefix, "json", with_timestamp)
        with open(out_path, "w") as f:
            json.dump(data, f)
        self.logger.debug("Exported data to json.")

    def format(self, data: list, data2: list, timestamp: list) -> list:
        formatted_data = []
        for data, data2, timestamp in zip(data, data2, timestamp):
            formatted_data.append(
                {"timestamp": timestamp, "value": data, "failed": data2}
            )
        return formatted_data
