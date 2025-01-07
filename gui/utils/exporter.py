"""GUIアプリケーション用の出力機能"""

from cores.export_utils import export, build_data_records
from cores.common import filter_dict
from typing import Dict


def export_result(data: Dict) -> None:
    """
    推論結果のエクスポート処理

    Args:
        data (Dict): results, failed_rates, timestamps, format, out_dirを含む辞書
    """
    results = build_data_records(
        {
            "results": data["results"],
            "failed_rates": data["failed_rates"],
            "timestamps": data["timestamps"],
        }
    )
    export(results, data["format"], data["out_dir"], "result")


def export_settings(settings: Dict) -> None:
    """
    設定のエクスポート処理

    Args:
        settings (Dict): 設定情報を含む辞書
    """
    excluded_keys = {"results", "failed_rates", "timestamps", "first_frame", "frames"}
    filtered_settings = filter_dict(settings, lambda k, _: k not in excluded_keys)
    export(filtered_settings, "json", settings["out_dir"], "settings")
