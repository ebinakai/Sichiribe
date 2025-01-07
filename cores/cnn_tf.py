"""
TensorFlowを使用したCNNモデルの実装

このモジュールは、TensorFlowを用いて畳み込みニューラルネットワーク（CNN）の実装を行う機能を提供する

Requirements:
    - tensorflow: CNNモデルの構築と推論に使用

Alternative_Implementations:
    - cnn_tflite.py: TensorFlow Liteを使用したバージョン
    - cnn_onnx.py: ONNXを使用したバージョン

Notes:
    - TensorFlowがインストールされていない場合は、ライブラリをインストールするか、代替実装を利用すること
"""

try:
    from tensorflow.keras.models import load_model
except ImportError:
    pass

from cores.cnn import CNNCore
import os
import logging
from typing import TYPE_CHECKING, List
import numpy as np
from pathlib import Path

# TensorFlow と h5py のログを無効にする
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("h5py").setLevel(logging.ERROR)

if TYPE_CHECKING:
    from tensorflow.keras.models import Model

FILE = Path(__file__).resolve()
ROOT = FILE.parent / ".."


class CNNTf(CNNCore):
    """TensorFlow形式の学習済みモデルを使用したCNNクラス"""

    model: "Model"

    def __init__(self, num_digits: int, model_filename: str) -> None:
        super().__init__(num_digits)
        self.logger = logging.getLogger("__main__").getChild(__name__)

        # 学習済みモデルの絶対パスを取得
        model_path = ROOT / "model" / model_filename
        self.model_path = model_path.resolve()
        self.logger.debug("Load model path: %s" % self.model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        self.model = load_model(self.model_path)
        self.logger.info("CNN Model loaded.")

    def inference_7seg_classifier(self, image: np.ndarray) -> List[int]:
        """画像から7セグメント数字を推論する

        Args:
            image (np.ndarray): 推論対象の画像

        Returns:
            List[int]: 各桁の推論結果
        """
        # 各桁に分割
        preprocessed_images = self.preprocess_image(image)

        predictions = self.model.predict(
            np.array(preprocessed_images), verbose=0
        )  # verbose=0: ログ出力を抑制

        # 各行に対して最大値のインデックスを取得
        argmax_indices = predictions.argmax(axis=1)

        return argmax_indices
