from cores.cnn_core import CNNCore
import os
import logging
import numpy as np
from pathlib import Path
import onnxruntime as ort


class CNNOnnx(CNNCore):
    def __init__(self, num_digits, model_filename='model_100x100.onnx'):
        super().__init__(num_digits)
        self.logger = logging.getLogger('__main__').getChild(__name__)

        # 学習済みモデルの絶対パスを取得
        current_dir = Path(__file__).resolve().parent
        model_path = current_dir / '..' / 'model' / model_filename
        model_path = model_path.resolve()
        self.model_path = str(model_path)
        self.model = None
        self.session = None

    def load(self):
        self.logger.debug('Load model path: %s' % self.model_path)
        if not os.path.exists(self.model_path):
            self.logger.error('Model file not found.')
            return False

        if self.session is None:
            # ONNXランタイムセッションの作成
            self.session = ort.InferenceSession(self.model_path)
            self.input_name = self.session.get_inputs()[0].name
            self.logger.info("ONNX Model loaded.")
        return True

    def inference_7seg_classifier(self, image: np.ndarray) -> list:
        # 各桁に分割
        preprocessed_images = self.preprocess_image(image)

        predictions = []
        for preprocessed_image in preprocessed_images:
            img_ = np.expand_dims(preprocessed_image, axis=0)  # バッチサイズの次元を追加

            # ONNX推論
            output = self.session.run(None, {self.input_name: img_})[0]
            predictions.append(output)

        # (num_digits, num_classes) 形状に変換
        predictions = np.array(predictions).squeeze()
        argmax_indices = predictions.argmax(axis=1)  # 各行に対して最大値のインデックスを取得

        return argmax_indices
