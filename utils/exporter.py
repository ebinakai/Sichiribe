import logging
import json
import datetime
import os
from utils.common import get_now_str

# ロガーの設定
logger = logging.getLogger("__main__").getChild(__name__)

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
    
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(out_dir, exist_ok=True)
    
    if method == 'csv':
        self.save = self.to_csv
    elif method == 'json':
        self.save = self.to_json
    else:
      logger.error("Invalid export method.")
        
    logger.debug("Exporter loaded.")

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
    out_path = self.generate_filepath("csv")
    with open(out_path, 'w') as f:
      f.write('timestamp,result\n')
      for i, _data in enumerate(data):
        f.write(f"{_data['timestamp']},{_data['value']}\n")
    logger.debug("Exported data to csv.")
  
  # json形式で保存
  def to_json(self, data):
    out_path = self.generate_filepath("json")
    with open(out_path, 'w') as f:
      json.dump(data, f)
    logger.debug("Exported data to json.")
    
  # データを辞書型に整形
  def format(self, data, timestamp):
    formatted_data = []
    for data, timestamp in zip(data, timestamp):
      formatted_data.append({"timestamp": timestamp, "value": data})
    return formatted_data