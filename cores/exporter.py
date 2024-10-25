import logging
import json
import csv
import os
from typing import Union
from cores.common import get_now_str


def get_supported_formats() -> list:
    return Exporter.aveilable_formats


class Exporter:
    # インスタンス化しなくてもサポートフォーマットを取得するためにクラス変数として定義
    aveilable_formats = ['csv', 'json']

    def __init__(self, method: str, out_dir: str,
                 base_filename: str = 'result'):
        self.method = method
        self.base_filename = base_filename
        self.out_dir = out_dir
        self.logger = logging.getLogger("__main__").getChild(__name__)

        if method in self.aveilable_formats:
            os.makedirs(out_dir, exist_ok=True)

        if method == 'csv':
            self.save = self.to_csv
        elif method == 'json':
            self.save = self.to_json
        elif method == 'dummy':
            self.save = self.to_dummy
        else:
            self.logger.error("Invalid export method.")

        self.logger.debug("Exporter loaded.")

    def export(self, data: Union[list, dict]) -> None:
        self.save(data)

    # ファイル名を時刻を含めて生成
    def generate_filepath(self, extension: str) -> str:
        now = get_now_str()
        filename = f"{self.base_filename}_{now}.{extension}"
        return os.path.join(self.out_dir, filename)

    def to_csv(self, data: list) -> None:
        if not data:
            self.logger.debug("No data to export.")
            return
        out_path = self.generate_filepath("csv")
        keys = data[0].keys()
        with open(out_path, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        self.logger.debug("Exported data to csv.")

    def to_json(self, data: Union[dict, list]) -> None:
        if not data:
            self.logger.debug("No data to export.")
            return
        out_path = self.generate_filepath("json")
        with open(out_path, 'w') as f:
            json.dump(data, f)
        self.logger.debug("Exported data to json.")

    def to_dummy(self, data) -> None:
        self.logger.debug("No exported data, it's dummy.")

    def format(self, data: list, data2: list, timestamp: list) -> list:
        formatted_data = []
        for data, data2, timestamp in zip(data, data2, timestamp):
            formatted_data.append(
                {"timestamp": timestamp, "value": data, "failed": data2})
        return formatted_data

    def filter_dict(self, dic: dict, excluded_keys: list) -> dict:
        filtered_params = {
            k: v for k,
            v in dic.items() if k not in excluded_keys}
        return filtered_params
