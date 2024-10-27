'''
GUIアプリケーションにおいて、画面間で共有されるパラメータを使用して結果をエクスポートするためモジュール
'''

from cores.exporter import Exporter
from cores.common import filter_dict


def export_result(params: dict) -> None:
    ep = Exporter(params['out_dir'])
    data = ep.format(
        params['results'],
        params['failed_rates'],
        params['timestamps'])
    ep.export(data, method=params['format'])


def export_params(params: dict) -> None:
    ep = Exporter(out_dir=params['out_dir'])
    excluded_keys = {
        'results',
        'failed_rates',
        'timestamps',
        'first_frame',
        'frames'}
    filtered_params = filter_dict(params, lambda k, _: k not in excluded_keys)
    ep.export(filtered_params, method='json', base_filename='parameters')
