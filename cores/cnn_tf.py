from cores.cnn_core import CNNCore
import os
import logging
import numpy as np
from pathlib import Path

# TensorFlow と h5py のログを無効にする
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('h5py').setLevel(logging.ERROR)


class CNN(CNNCore):
    def __init__(self, num_digits,
                 model_filename='model_100x100.keras') -> None:
        super().__init__(num_digits)
        self.logger = logging.getLogger("__main__").getChild(__name__)

        # 学習済みモデルの絶対パスを取得
        current_dir = Path(__file__).resolve().parent
        model_path = current_dir / '..' / 'model' / model_filename
        model_path = model_path.resolve()
        self.model_path = str(model_path)

    def load(self) -> bool:
        self.logger.debug('Load model path: %s' % self.model_path)
        if not os.path.exists(self.model_path):
            self.logger.error('Model file not found.')
            return False

        if self.model is None:
            from tensorflow.keras.models import load_model
            self.model = load_model(self.model_path)
        self.logger.info("CNN Model loaded.")
        return True

    def inference_7seg_classifier(self, image: np.ndarray) -> list[int]:
        # 各桁に分割
        preprocessed_images = self.preprocess_image(image)

        predictions = self.model.predict(
            np.array(preprocessed_images),
            verbose=0)  # verbose=0: ログ出力を抑制

        argmax_indices = predictions.argmax(axis=1)  # 各行に対して最大値のインデックスを取得

        return argmax_indices
