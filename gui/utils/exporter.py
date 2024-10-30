"""
GUIアプリケーションにおいて、画面間で共有されるパラメータを使用して結果をエクスポートするためモジュール
"""

from cores.export_utils import export, build_data_records
from cores.common import filter_dict
from typing import Dict


def export_result(data: Dict) -> None:
    results = build_data_records(
        {
            "results": data["results"],
            "failed_rates": data["failed_rates"],
            "timestamps": data["timestamps"],
        }
    )
    export(results, data["format"], data["out_dir"], "result")


def export_settings(settings: Dict) -> None:
    excluded_keys = {"results", "failed_rates", "timestamps", "first_frame", "frames"}
    filtered_settings = filter_dict(settings, lambda k, _: k not in excluded_keys)
    export(filtered_settings, "json", settings["out_dir"], "settings")
