import logging
import json
import csv
import os
from typing import Union, List, Dict, Any
from cores.common import get_now_str


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
        self, data: List[Any] | Dict, method: str, base_filename: str = "result"
    ) -> None:
        if method == "csv":
            self.to_csv(data, base_filename)
        elif method == "json":
            self.to_json(data, base_filename)
        elif method == "dummy":
            pass
        else:
            self.logger.error("Invalid export method.")

    # ファイル名を時刻を含めて生成
    def generate_filepath(self, base_filename: str, extension: str) -> str:
        now = get_now_str()
        filename = f"{base_filename}_{now}.{extension}"
        return os.path.join(self.out_dir, filename)

    def to_csv(self, data: List[Dict] | List | Dict, base_filename: str) -> None:
        if not data:
            self.logger.debug("No data to export.")
            return
        out_path = self.generate_filepath(base_filename, "csv")
        keys = data[0].keys()
        with open(out_path, "w", newline="") as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        self.logger.debug("Exported data to csv.")

    def to_json(self, data: Union[Dict, List], base_filename: str) -> None:
        if not data:
            self.logger.debug("No data to export.")
            return
        out_path = self.generate_filepath(base_filename, "json")
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
