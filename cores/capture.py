import cv2
import time
import logging

class FrameCapture:
  def __init__(
        self, 
        device_num=0,
    ):
    
    self.logger = logging.getLogger("__main__").getChild(__name__)

    self.cap = cv2.VideoCapture(device_num)
    self.frame_count = 0
    
    # カメラに接続するまで待機
    time.sleep(0.1)

  def show_camera_feed(self):

    while True:
      frame = self.capture()
      if frame is None:
        break

      window_title = "Press 'Y' to finish."
      cv2.imshow(window_title, frame)

      # 'q' キーが押されたらループを抜ける
      if cv2.waitKey(1) & 0xFF == ord('y'):
        break

    cv2.destroyAllWindows()
    cv2.waitKey(1)

  def capture(self):
    ret, frame = self.cap.read()
    if ret:
      return frame
    else:
      self.logger.error("Failed to capture frame")

  def release(self):
    self.cap.release()
    cv2.destroyAllWindows()
    
  def set_cap_size(self, width, height):
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    self.logger.debug("set_cap_size called: {0} x {1}".format(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    self.logger.debug("set to {0} x {1}".format(width, height))
    return width, height
    