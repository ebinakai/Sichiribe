from tflite_runtime import interpreter as tflite
from cores.cnn import CNNCore
import os
import logging
from typing import TYPE_CHECKING, List, Any, Dict
import numpy as np
from pathlib import Path

# TensorFlow と h5py のログを無効にする
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("h5py").setLevel(logging.ERROR)

if TYPE_CHECKING:
    from tflite_runtime.interpreter import Interpreter

FILE = Path(__file__).resolve()
ROOT = FILE.parent / ".."


class CNNLite(CNNCore):
    """TensorFlow Lite形式の学習済みモデルを使用したCNNクラス
    """

    model: "Interpreter"
    input_details: List[Dict[str, Any]]
    output_details: List[Dict[str, Any]]

    def __init__(self, num_digits: int, model_filename: str) -> None:
        super().__init__(num_digits)
        self.logger = logging.getLogger("__main__").getChild(__name__)

        # 学習済みモデルの絶対パスを取得
        model_path = ROOT / "model" / model_filename
        self.model_path = model_path.resolve()
        self.logger.debug("Load model path: %s" % self.model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        # TensorFlow Lite モデルの読み込み
        self.model = tflite.Interpreter(model_path=self.model_path)
        self.model.allocate_tensors()
        self.input_details = self.model.get_input_details()
        self.output_details = self.model.get_output_details()
        self.logger.info("TFLite Model loaded.")

    # 画像から数字を推論
    def inference_7seg_classifier(self, image: np.ndarray) -> List[int]:
        """画像から7セグメント数字を推論する
        
        Args:
            image (np.ndarray): 推論対象の画像
            
        Returns:
            List[int]: 各桁の推論結果
        """
        # 各桁に分割
        preprocessed_images = self.preprocess_image(image)

        # 1桁ずつ処理
        predictions = []
        for preprocessed_image in preprocessed_images:
            img_ = np.expand_dims(
                preprocessed_image, axis=0
            )  # バッチサイズの次元を追加

            self.model.set_tensor(self.input_details[0]["index"], img_)
            self.model.invoke()
            output_data = self.model.get_tensor(self.output_details[0]["index"])
            predictions.append(output_data)

        # (num_digits, num_classes) 形状に変換
        predictions_ = np.array(predictions).squeeze()

        # 各行に対して最大値のインデックスを取得
        argmax_indices = predictions_.argmax(axis=1)

        return argmax_indices
