from cores.cnn import CNNCore
import logging
from typing import TYPE_CHECKING
import numpy as np
from pathlib import Path
import onnxruntime as ort

if TYPE_CHECKING:
    from onnxruntime.capi.onnxruntime_inference_collection import InferenceSession


class CNNOnnx(CNNCore):
    model: "InferenceSession"

    def __init__(self, num_digits: int, model_filename: str) -> None:
        super().__init__(num_digits)
        self.logger = logging.getLogger("__main__").getChild(__name__)

        # 学習済みモデルの絶対パスを取得
        current_dir = Path(__file__).resolve().parent
        model_path = current_dir / ".." / "model" / model_filename
        self.model_path = model_path.resolve()
        self.logger.debug(f"Load model path: {self.model_path}")

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        # ONNXランタイムセッションの作成
        self.model = ort.InferenceSession(self.model_path)
        self.input_name = self.model.get_inputs()[0].name
        self.logger.info("ONNX Model loaded.")

    def inference_7seg_classifier(self, image):
        # 各桁に分割
        preprocessed_images = self.preprocess_image(image)

        predictions = []
        for preprocessed_image in preprocessed_images:
            img_ = np.expand_dims(
                preprocessed_image, axis=0
            )  # バッチサイズの次元を追加

            # ONNX推論
            output = self.model.run(None, {self.input_name: img_})[0]
            predictions.append(output)

        # (num_digits, num_classes) 形状に変換
        predictions_ = np.array(predictions).squeeze()
        argmax_indices = predictions_.argmax(
            axis=1
        )  # 各行に対して最大値のインデックスを取得

        return argmax_indices
