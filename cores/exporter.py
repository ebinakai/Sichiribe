import logging
import json
import csv
import os
from cores.common import get_now_str

# クラス外部で使用可能なサポートフォーマットを取得する関数
def get_supported_formats():
  return Exporter.aveilable_formats

class Exporter:
  # クラス変数としてサポートフォーマットを定義
  aveilable_formats = ['csv', 'json']
  
  def __init__(self, method, out_dir, base_filename='result'):
    self.method = method
    self.base_filename = base_filename
    self.out_dir = out_dir
    
    # ロガーの設定
    self.logger = logging.getLogger("__main__").getChild(__name__)
    
    # 出力ディレクトリが存在しない場合は作成
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

  # データを保存
  def export(self, data):
    self.save(data)
  
  # ファイル名を時刻を含めて生成
  def generate_filepath(self, extension):
    now = get_now_str()
    filename = f"{self.base_filename}_{now}.{extension}"
    return os.path.join(self.out_dir, filename)

  # csv形式で保存
  def to_csv(self, data):
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
  
  # json形式で保存
  def to_json(self, data):
    if not data:
        self.logger.debug("No data to export.")
        return
    out_path = self.generate_filepath("json")
    with open(out_path, 'w') as f:
      json.dump(data, f)
    self.logger.debug("Exported data to json.")
    
  # 出力しない
  def to_dummy(self, data):
    self.logger.debug("No exported data, it's dummy.")
    
  # データを辞書型に整形
  def format(self, data, timestamp):
    formatted_data = []
    for data, timestamp in zip(data, timestamp):
      formatted_data.append({"timestamp": timestamp, "value": data})
    self.logger.debug("formatted data: %s", formatted_data)
    return formatted_data
  
  def format(self, data, data2, timestamp):
    formatted_data = []
    for data, data2, timestamp in zip(data, data2, timestamp):
      formatted_data.append({"timestamp": timestamp, "value": data, "failed": data2})
    self.logger.debug("formatted data: %s", formatted_data)
    return formatted_data