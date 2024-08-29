import cv2
import time
import logging

logger = logging.getLogger("__main__").getChild(__name__)

class FrameCapture:
  def __init__(
        self, 
        device_num=0,
    ):

    self.cap = cv2.VideoCapture(device_num)
    self.frame_count = 0
    
    # カメラに接続するまで待機
    time.sleep(0.1)
    
  def show_camera_feed(self):

    while True:
      # フレームが正しくキャプチャされているかを確認
      frame = self.capture()
      if frame is None:
        break

      # フレームをウィンドウに表示
      window_title = "Press 'Y' to finish."
      cv2.imshow(window_title, frame)

      # 'q' キーが押されたらループを抜ける
      if cv2.waitKey(1) & 0xFF == ord('y'):
        break

    # ウィンドウを閉じる
    cv2.destroyAllWindows()
    cv2.waitKey(1)

  def capture(self):
    ret, frame = self.cap.read()
    if ret:
      return frame
    else:
      logger.error("Failed to capture frame")

  def release(self):
    self.cap.release()
    cv2.destroyAllWindows()
