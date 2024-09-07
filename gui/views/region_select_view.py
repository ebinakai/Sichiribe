import logging
import numpy as np
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSizePolicy
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtCore import Qt, QSize, QTimer
from gui.utils.screen_manager import ScreenManager
from cores.frameEditor import FrameEditor
from gui.utils.common import convert_cv_to_qimage, resize_image

class ClickableLabel(QLabel):
    # コールバック関数はマウスイベント内で呼び出され、イベントが引き継がれる
    def __init__(self, parent=None, handle_event=lambda x: x):
        super().__init__(parent)
        self.handle_event = handle_event
        self.drawing = False
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()
            self.handle_event(event)
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drawing:
            current_point = event.position().toPoint()
            self.handle_event(event)
            self.last_point = current_point
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

class RegionSelectWindow(QWidget):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__()
        
        self.logger = logging.getLogger('__main__').getChild(__name__)
        
        self.screen_manager = screen_manager
        screen_manager.add_screen('region_select', self)
        self.click_points = []
        
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        self.target_width = int(screen_rect.width() * 0.8)
        self.target_height = int((screen_rect.height() - 100) * 0.8)
        self.initUI()
        
    def initUI(self):
        # メインウィジェットの設定
        main_layout = QVBoxLayout()
        header_layout = QVBoxLayout()
        image_layout = QVBoxLayout()
        extracted_image_layout = QHBoxLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        extracted_image_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # ヘッダーレイアウト
        self.header_description = QLabel("7セグメント領域として4点を選択してください")
        header_layout.addWidget(self.header_description)
        
        # 画像を表示するためのラベル
        self.main_label = ClickableLabel(self, self.label_clicked)
        # サイズポリシーを設定して、ラベルが画像サイズに合わせて変わるようにする
        self.main_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        image_layout.addWidget(self.main_label)
        
        # 選択領域表示用レイアウト
        self.extracted_label = QLabel()
        self.extracted_label.setMinimumHeight(100)
        extracted_image_layout.addWidget(self.extracted_label)
        
        # フッターレイアウト
        # 「戻る」ボタン
        self.back_button = QPushButton('戻る')
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(self.cancel_select)
        footer_layout.addWidget(self.back_button)

        footer_layout.addStretch()  # スペーサーを追加してボタンを右寄せ

        # 次へボタンとコンファームテキスト
        footer_right_layout = QHBoxLayout()
        self.confirm_txt = QLabel()
        self.confirm_txt.setStyleSheet('color: red')
        footer_right_layout.addWidget(self.confirm_txt)
        self.next_button = QPushButton('次へ')
        self.next_button.setDefault(True)  # 強調表示されるデフォルトボタンに設定
        self.next_button.setAutoDefault(True)  # フォーカス時にエンターキーで実行
        self.next_button.setFixedWidth(100)
        self.next_button.clicked.connect(self.finish_select)
        footer_right_layout.addWidget(self.next_button)  # 次へボタンを追加

        footer_layout.addLayout(footer_right_layout)  # フッターレイアウトに追加
        
        # メインレイアウトに追加
        main_layout.addLayout(header_layout)
        main_layout.addLayout(image_layout)
        main_layout.addLayout(extracted_image_layout)
        main_layout.addLayout(footer_layout)
    
    def set_image(self, image: np.ndarray):
        self.image_original = image
        self.image, self.resize_scale = resize_image(image, self.target_width, self.target_height)
        
        self.update_image(self.image.copy())
        
    def label_clicked(self, event: QMouseEvent):
        if  event.button() == Qt.MouseButton.LeftButton or \
            event.button() == Qt.MouseButton.NoButton and len(self.click_points) == 4:
            
            # QLabel内の座標を取得
            label_pos = event.position().toPoint()
            
            if  label_pos.x() <= 0 or \
                label_pos.x() >= self.image_size.width() or \
                label_pos.y() <= 0 or \
                label_pos.y() >= self.image_size.height():
                return
            
            new_point = np.array([label_pos.x(), label_pos.y()]).astype(np.int32)
            
            if len(self.click_points) < 4:
                # 4点未満なら普通に追加
                self.click_points.append(new_point)
            else:
                # 4点以上の場合、最も近い点を入れ替える
                distances = np.linalg.norm(np.array(self.click_points) - new_point, axis=1)
                closest_index = np.argmin(distances)
                self.click_points[closest_index] = new_point
                
            if len(self.click_points) == 4:
                self.click_points = self.fe.order_points(self.click_points)
            
            self.update_image(self.image.copy())
        
    def display_image(self, image: np.ndarray):
        q_image = convert_cv_to_qimage(image)
        self.main_label.setPixmap(QPixmap.fromImage(q_image))
        self.main_label.adjustSize()  # ラベルを画像サイズに調整
        
    def display_extract_image(self, image: np.ndarray):
        q_image = convert_cv_to_qimage(image)
        self.extracted_label.setPixmap(QPixmap.fromImage(q_image))
        
    def update_image(self, image):
        extract_image = self.fe.crop(self.image_original, np.array(self.click_points) / self.resize_scale)
        image, extract_image = self.fe.draw_debug_info(image, extract_image, self.click_points)
        height, width, channel = self.image.shape
        self.image_size = QSize(width, height)
        self.display_image(image)
        
        if extract_image is not None:
            self.display_extract_image(extract_image)
        
    def startup(self, params, prev_screen):
        self.logger.info('Starting RegionSelectWindow.')
        self.params = params
        self.prev_screen = prev_screen
        self.fe = FrameEditor(num_digits=params['num_digits'])
        
        # ウィンドウの位置とサイズを保存
        window_pos, window_size = self.screen_manager.save_screen_size()
        
        # 表示画像サイズを計算
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        self.target_width = int(screen_rect.width() * 0.8)
        self.target_height = int((screen_rect.height() - 100) * 0.8)
        
        self.set_image(params['first_frame'])
        self.screen_manager.show_screen('region_select')
        QTimer.singleShot(1, lambda: self.window().move(window_pos.x(), 0))
        
    def finish_select(self):
        if len(self.click_points) != 4:
            self.confirm_txt.setText('7セグメント領域を囲ってください')
            return
        
        self.logger.info("Region selection finished.")
        click_points = np.array(self.click_points) / self.resize_scale
        self.params['click_points'] = click_points.tolist()
        
        # 現在のページのウィジェットの設定をリセット
        self.clear_env()

        # ウィンドウサイズの適用を待ってから次の画面に遷移
        QTimer.singleShot(1, self.switch_next)
    
    def cancel_select(self):
        self.logger.info("Region selection canceled.")
        self.clear_env()
        QTimer.singleShot(1, lambda: self.switch_back())
    
    def switch_back(self):
        self.logger.debug("Switching to back screen(%s).", self.prev_screen)
        if self.prev_screen == 'replay_exe':
            self.screen_manager.show_screen('replay_setting')
        elif self.prev_screen == 'live_feed':
            self.screen_manager.get_screen('live_feed').startup(self.params)
        self.prev_screen = None
        self.params = None

    def switch_next(self):
        self.logger.debug("Switching to next screen(%s).", self.prev_screen)
        if self.prev_screen == 'replay_exe':
            self.screen_manager.get_screen('replay_exe').frame_devide_process(self.params)
        elif self.prev_screen == 'live_feed':
            self.screen_manager.get_screen('live_exe').startup(self.params)
        self.prev_screen = None
        self.params = None

    def clear_env(self):
        self.main_label.clear()
        self.extracted_label.clear()
        self.target_width = None
        self.target_height = None
        self.image = None
        self.image_original = None
        self.click_points = []
        self.confirm_txt.setText('')
        self.fe = None
        self.logger.info('Environment cleared.')

        # ウィンドウサイズを元に戻す
        # QTimer.singleShot(1, self.screen_manager.restore_screen_size)
