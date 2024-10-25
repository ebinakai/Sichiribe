'''
GUIアプリケーションにおいて、画面間で共有されるパラメータを使用して結果をエクスポートするためモジュール
'''

from cores.exporter import Exporter


def export_result(params: dict) -> None:
    ep = Exporter(params['format'], params['out_dir'])
    data = ep.format(
        params['results'],
        params['failed_rates'],
        params['timestamps'])
    ep.export(data)


def export_params(params: dict) -> None:
    ep = Exporter(
        method='json',
        out_dir=params['out_dir'],
        base_filename='parameters')
    filtered_params = ep.filter_dict(
        params, ['results', 'failed_rates', 'timestamps', 'first_frame', 'frames'])
    ep.export(filtered_params)
