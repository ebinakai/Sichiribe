import cv2

class RegionSelector:
  def __init__(self, image_path):
    self.start_x, self.start_y = -1, -1
    self.rectangles = ()
    self.selection_done = False
    self.img = cv2.imread(image_path)
    self.clone = self.img.copy()
    
  def get_selected_rect(self):
    return self.rectangles

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
        
        # 選択範囲座標の取得
        self.rectangles = (
            min(self.start_x, end_x),
            min(self.start_y, end_y),
            max(self.start_x, end_x),
            max(self.start_y, end_y)
        )
        
        cv2.rectangle(
          self.img, (self.start_x, self.start_y), (end_x, end_y), (0, 255, 0), 2
        )
        cv2.imshow("Image", self.img)

        # 選択された範囲の座標を表示
        print(
          f"Selected region: ({self.start_x}, {self.start_y}) - ({end_x}, {end_y})"
        )

        # 選択が確定したので、選択状態フラグを設定
        self.selection_done = True

  def run(self):
    cv2.imshow("Image", self.img)
    cv2.setMouseCallback("Image", self.mouse_callback)

    # ユーザーがウィンドウを閉じるまで待機
    while not self.selection_done:
      cv2.waitKey(100)  # 100ミリ秒ごとにキー入力を待機

    cv2.destroyAllWindows()

if __name__ == '__main__':
  # 使用例
  from videoCrop import frameCrop
  file_path = "frames/frame_0000.jpg"
  selector = RegionSelector(file_path)
  selector.run()
  frameCrop(file_path, selector.get_selected_rect(), gray_scale=True)