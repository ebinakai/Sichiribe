import easyocr
import cv2
import pprint

# 文字の選択一回だけでいい
reader = easyocr.Reader(['en'])

# 画像表示用関数
def showImage(image, message="image showing"):
  cv2.imshow(message, image)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
  

# file_path = 'images/7seg_numonly.jpeg'
file_path = 'images/7seg_trimmed.jpeg'

# 画像の読み込み
image_gs = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

# 二値化（しきい値を調整する）
_, image_bin = cv2.threshold(image_gs, 100, 255, cv2.THRESH_BINARY_INV)

# 二値化された画像をカラーに変換
image_cl = cv2.cvtColor(image_bin, cv2.COLOR_GRAY2BGR)

result = reader.readtext(image_cl)
pprint.pprint(result)

img_1 = image_cl.copy()

for i in range(len(result)):
    # バウンディングボックスの描画
    cv2.rectangle(img_1, tuple(result[i][0][0]), tuple(result[i][0][2]), (0, 255, 0), 3)
    
    # インデックスラベルの描画
    label_position = tuple(result[i][0][0])  # バウンディングボックスの左上を基準に
    cv2.putText(img_1, str(i), (label_position[0], label_position[1] - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

# 画像を表示する
showImage(img_1)
