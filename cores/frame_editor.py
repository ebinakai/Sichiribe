import os
from typing import Union, List
import cv2
import logging
import numpy as np
from datetime import timedelta
from cores.common import clear_directory


class FrameEditor:
    def __init__(self,
                 sampling_sec: int = 3,
                 num_frames_per_sample: int = 10,
                 num_digits: int = 4,
                 crop_width: int = 100,
                 crop_height: int = 100,
                 ) -> None:

        self.return_frames = []
        self.sampling_sec = sampling_sec                   # サンプリング間隔（秒）
        self.num_frames_per_sample = num_frames_per_sample  # サンプリングするフレーム数
        self.num_digits = num_digits    # 読み取り桁数
        self.crop_width = crop_width    # 1文字ごとのクロップ幅
        self.crop_height = crop_height  # 1文字ごとのクロップ高さ
        self.click_points = []

        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.logger.debug("Frame Editor loaded.")

    # 動画をフレームに分割
    def frame_devide(self,
                     video_path: str,
                     skip_sec: int = 0,
                     save_frame: bool = True,
                     out_dir: str = 'frames',
                     is_crop: bool = True,
                     click_points: list = [],
                     extract_single_frame: bool = False,
                     ) -> Union[np.ndarray, List[List[Union[np.ndarray, str]]]]:
        self.click_points = click_points

        if save_frame:
            os.makedirs(out_dir, exist_ok=True)
            clear_directory(out_dir)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.logger.error("Error: Could not open video file.")
            exit(1)

        fps = cap.get(cv2.CAP_PROP_FPS)
        interval_frames = 1 if self.sampling_sec == 0 else int(
            fps * self.sampling_sec)
        skip_frames = fps * skip_sec
        frame_count = 0
        saved_frame_count = 0
        frames = []
        return_frames = []

        # 指定の開始位置までスキップ
        cap.set(cv2.CAP_PROP_POS_FRAMES, skip_frames)

        while True:
            ret, frame = cap.read()
            if not ret:
                self.logger.debug("Finsish: Could not read frame.")
                break

            # サンプリング間隔に基づいてフレームを保存
            if frame_count % interval_frames < self.num_frames_per_sample:
                if is_crop:

                    # フレームの切り取り
                    if len(self.click_points) != 4:
                        self.region_select(frame)
                    frame = self.crop(frame, self.click_points)

                # 最初の位置フレームだけ取得
                if extract_single_frame:
                    return_frames = frame
                    break

                if save_frame:
                    frame_filename = os.path.join(
                        out_dir, f'frame_{frame_count:06d}.jpg')
                    cv2.imwrite(frame_filename, frame)
                    saved_frame_count += 1
                    self.logger.debug(f"Frame saved to '{frame_filename}'.")

                    frames.append(frame_filename)
                else:
                    frames.append(frame)

            elif len(frames) != 0:
                return_frames.append(frames)
                frames = []

            frame_count += 1

        cap.release()
        self.logger.debug("Capture resources released.")

        if saved_frame_count > 0:
            self.logger.info(
                f"Extracted {saved_frame_count} frames were saved to '{out_dir}' directory.")

        return return_frames

    # 切り出したフレームの間隔からタイムスタンプを生成
    def generate_timestamp(self, n: int) -> list[str]:
        timestamps = []

        for i in range(0, n):
            timestamp = timedelta(seconds=self.sampling_sec * i)
            # タイムスタンプを "HH:MM:SS" 形式でリストに追加
            timestamps.append(str(timestamp))

        return timestamps

    # クリックポイント4点から画像を切り出す
    def crop(
        self,
        image: np.ndarray,
        click_points: Union[list, np.ndarray],
    ) -> np.ndarray:
        extract_image = None

        if len(click_points) == 4:
            # 射影変換
            pts1 = np.float32([
                click_points[0],
                click_points[1],
                click_points[2],
                click_points[3],
            ])
            pts2 = np.float32([
                [0, 0],
                [self.crop_width * self.num_digits, 0],
                [self.crop_width * self.num_digits, self.crop_height],
                [0, self.crop_height],
            ])
            M = cv2.getPerspectiveTransform(pts1, pts2)
            extract_image = cv2.warpPerspective(
                image, M, (self.crop_width * self.num_digits, self.crop_height))

        return extract_image

    def region_select(self, image: Union[str, np.ndarray]) -> np.ndarray:
        img = image if isinstance(image, np.ndarray) else cv2.imread(image)

        window_name = "Select 7seg Region"
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.mouse_callback)

        while True:
            img_clone = img.copy()

            extract_image = self.crop(img_clone, self.click_points)

            # デバッグ情報描画
            img_clone, extract_image = self.draw_debug_info(
                img_clone,
                extract_image,
                self.click_points,
            )

            # 描画更新
            cv2.imshow(window_name, img_clone)
            if extract_image is not None:
                cv2.imshow('Result', extract_image)

            key = cv2.waitKey(100)
            if key == ord('y') and len(self.click_points) == 4:  # yキーで選択終了
                cv2.destroyAllWindows()
                cv2.waitKey(1)
                return self.click_points if len(
                    self.click_points) == 4 else None

    def mouse_callback(self, event, x, y, flags, param) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            new_point = np.array([x, y])

            if len(self.click_points) < 4:
                self.click_points.append(new_point)
            else:
                # 4点以上の場合、最も近い点を入れ替える
                distances = np.linalg.norm(
                    np.array(
                        self.click_points) -
                    new_point,
                    axis=1)
                closest_index = np.argmin(distances)
                self.click_points[closest_index] = new_point

            if len(self.click_points) == 4:
                self.click_points = self.order_points(self.click_points)

    def order_points(self, points: Union[list, np.ndarray]) -> np.ndarray:
        points = np.array(points)

        # x座標で昇順にソート
        sorted_by_x = points[np.argsort(points[:, 0])]

        # 左側の2点と右側の2点に分ける
        left_points = sorted_by_x[:2]
        right_points = sorted_by_x[2:]

        # 左側の2点のうち、y座標が小さいものを左上、大きいものを左下とする
        left_points = left_points[np.argsort(left_points[:, 1])]
        top_left, bottom_left = left_points

        # 右側の2点のうち、y座標が小さいものを右上、大きいものを右下とする
        right_points = right_points[np.argsort(right_points[:, 1])]
        top_right, bottom_right = right_points

        return np.array([top_left, top_right, bottom_right, bottom_left])

    # 選択領域の可視化
    def draw_debug_info(
        self,
        image: np.ndarray,
        extract_image: np.ndarray,
        click_points_: Union[list, np.ndarray],
    ) -> tuple[np.ndarray, np.ndarray]:
        for click_point in click_points_:
            cv2.circle(
                image, (click_point[0], click_point[1]), 5, (0, 255, 0), -1
            )
        if len(click_points_) >= 3:
            cv2.drawContours(
                image, [np.array(click_points_)], -1, (0, 255, 0), 2
            )
        if extract_image is not None:
            for index in range(self.num_digits):
                temp_x = int(
                    (extract_image.shape[1] / self.num_digits) * index)
                temp_y = extract_image.shape[0]

                if index > 0:
                    cv2.line(extract_image, (temp_x, 0), (temp_x, temp_y),
                             (0, 255, 0), 1)
        return image, extract_image
