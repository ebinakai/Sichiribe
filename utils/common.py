import os
import shutil
import logging

logger = logging.getLogger("__main__").getChild(__name__)

def clear_directory(directory):
  # ディレクトリが存在するか確認
  if not os.path.exists(directory):
    logger.debug(f"The specified directory does not exist: {directory}")
    return

  # ディレクトリ内の全ファイルとサブディレクトリを削除
  for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    try:
      if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)  # ファイルまたはシンボリックリンクを削除
      elif os.path.isdir(file_path):
        shutil.rmtree(file_path)  # ディレクトリを再帰的に削除
    except Exception as e:
      logger.error(f"Failed to delete {file_path}. Reason: {e}")

  logger.debug(f"All contents in the directory '{directory}' have been deleted.")


def ask_user_confirmation(prompt):
  while True:
    answer = input(f"{prompt} (y/n): ").strip().lower()
    if answer in ['y', 'n']:
      return answer == 'y'
    print("Please answer with 'y' or 'n'.")