from PIL import Image
import pyocr
import pyocr.builders
import cv2
import sys

# file_path = 'images/7seg_numonly.jpeg'
file_path = 'images/7seg_trimmed.jpeg'

# ツール読み込み
tools = pyocr.get_available_tools()

# ツールが見付からない場合
if len(tools) == 0:
    print('pyocrが見付かりません。pyocrをインストールして下さい。')
    sys.exit(1)
tool = tools[0]

# 画像読み込み
image = Image.open(file_path)

txt1 = tool.image_to_string(
    image,
    lang='jpn+eng',
    builder=pyocr.builders.TextBuilder(tesseract_layout=6)
)
print(txt1)
     
results = tool.image_to_string(
    image,
    lang='jpn+eng',
    builder=pyocr.builders.WordBoxBuilder(tesseract_layout=6)
)

draw_rectangle = cv2.imread(file_path)

for box in results:
    print(box)
    #  左上、右下の点
    cv2.rectangle(draw_rectangle, box.position[0], box.position[1], (255, 0, 0), 1)

# 画像の保存
cv2.imwrite('draw_rectangle.png', draw_rectangle)
# 保存済みの画像を表示
draw_rectangle = Image.open('draw_rectangle.png')
draw_rectangle
