import logging
import cv2

logger = logging.getLogger("__main__").getChild(__name__)

class RegionSelector:
  def __init__(self):
    self.start_x, self.start_y = -1, -1
    self.rectangles = ()
    self.selection_done = False
    
    logger.debug("Legion Selector Loaded.")
    
  def mouse_callback(self, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
      self.start_x, self.start_y = x, y
      self.rectangles = ()          # 新しい選択のためにリセット
      self.clone = self.img.copy()  # 現在の画像をコピーして選択範囲を描画
      self.selection_done = False   # 選択がまだ確定していない

    elif event == cv2.EVENT_MOUSEMOVE:
      if self.start_x != -1 and self.start_y != -1:
        img = self.clone.copy()  # クローン画像を再度コピー
        end_x, end_y = x, y
        cv2.rectangle(
          img, (self.start_x, self.start_y), (end_x, end_y), (0, 255, 0), 2
        )
        cv2.imshow("Image", img)

    elif event == cv2.EVENT_LBUTTONUP:
      end_x, end_y = x, y
      
      # 選択範囲が無効な(ただクリックした)場合は何もしない
      if end_x == self.start_x and end_y == self.start_y:
        self.start_x, self.start_y = -1, -1
        return
      
      img = self.clone.copy()  # クローン画像を再度コピー
      
      # 選択範囲座標の取得
      self.rectangles = (
          min(self.start_x, end_x),
          min(self.start_y, end_y),
          max(self.start_x, end_x),
          max(self.start_y, end_y)
      )
      
      cv2.rectangle(
        img, (self.start_x, self.start_y), (end_x, end_y), (0, 255, 0), 2
      )
      cv2.imshow("Image", img)

      # 選択された範囲の座標を表示
      logger.info(f"Selected region: ({self.start_x}, {self.start_y}) - ({end_x}, {end_y})")

      # 選択が確定したので、選択状態フラグを設定
      self.selection_done = True

  def run(self, image_path):
    self.img = cv2.imread(image_path)
    self.clone = self.img.copy()
    
    while True:
      cv2.imshow("Image", self.img)
      cv2.setMouseCallback("Image", self.mouse_callback)

      # ユーザーがウィンドウを閉じるまで待機
      while not self.selection_done:
        cv2.waitKey(50)  # 100ミリ秒ごとにキー入力を待機

      cv2.destroyAllWindows()
      cv2.waitKey(1) # ウィンドウを閉じるために追加
      
      # 選択された範囲をクロップ
      x1, y1, x2, y2 = self.rectangles
      cropped_img = self.clone[y1:y2, x1:x2]

      # クロップされた画像を表示
      cv2.imshow("Cropped Image", cropped_img)
      print("Is this selection correct? Press 'y' to confirm, 'n' to select again.")
      key = cv2.waitKey(0)

      if key == ord('y'):
        cv2.destroyAllWindows()
        cv2.waitKey(1) # ウィンドウを閉じるために追加
        
        logger.info("Selected region: %s", self.rectangles)
        return self.rectangles
      elif key == ord('n'):
        # 選択をやり直す
        self.selection_done = False
        self.start_x, self.start_y = -1, -1
        cv2.destroyAllWindows()
        cv2.waitKey(1) # ウィンドウを閉じるために追加

if __name__ == '__main__':
  # 使用例
  file_path = "frames/frame_002759.jpg"
  sr = RegionSelector()
  sr.run(file_path)