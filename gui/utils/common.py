"""
雑多な関数をまとめたモジュール
"""

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QWidget
import numpy as np
import cv2
from platformdirs import user_data_dir


def convert_cv_to_qimage(cv_img: np.ndarray) -> QImage:
    height, width, channels = cv_img.shape

    # 画像が BGR 形式の場合
    if channels == 3:
        bytes_per_line = 3 * width
        qimage = QImage(
            cv_img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
        )
        return qimage.rgbSwapped()  # OpenCV uses BGR, QImage expects RGB

    # 画像が RGBA 形式の場合
    elif channels == 4:
        bytes_per_line = 4 * width
        qimage = QImage(
            cv_img.data, width, height, bytes_per_line, QImage.Format.Format_RGBA8888
        )
        return qimage

    else:
        raise ValueError(f"Unsupported number of channels: {channels}")


def resize_image(
    image: np.ndarray, target_width: float, target_height: float
) -> tuple[np.ndarray, float]:

    height, width = image.shape[:2]
    resize_scale_width = float(target_width / width)
    resize_scale_height = float(target_height / height)
    aspect_ratio = height / width

    # 短辺に合わせてアスペクト比を維持してリサイズ
    if resize_scale_width < resize_scale_height:
        resize_scale = resize_scale_width
        target_width = int(target_height)
        target_height = int(target_width * aspect_ratio)
    else:
        resize_scale = resize_scale_height
        target_width = int(target_height / aspect_ratio)
        target_height = int(target_height)

    resized_image = cv2.resize(
        image, (target_width, target_height), interpolation=cv2.INTER_AREA
    )

    return resized_image, resize_scale


def center_window(window: QWidget) -> None:
    screen = QApplication.primaryScreen()
    screen_rect = screen.availableGeometry()
    window_rect = window.frameGeometry()

    x = (screen_rect.width() - window_rect.width()) // 2
    y = (screen_rect.height() - window_rect.height()) // 2

    window.move(x, y)


def get_user_data_dir() -> str:
    appname = "Sichiribe"
    appauthor = "EbinaKai"
    return user_data_dir(appname, appauthor)
