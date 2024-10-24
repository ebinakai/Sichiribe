'''
matplotlibを使用してグラフを描画するためのカスタムウィジェット

1. matplotlibのバックエンドをQt5Aggに設定することでQtとの連携を行う
2. 以下のメソッドを提供する
    - MplCanvas: matplotlibのFigureを表示するためのカスタムウィジェット
    - gen_graph: グラフの初期化
    - update_existing_plot: 既存のプロットを更新
    - clear: グラフをクリア
'''

# Pillow と matplotlib のログを無効にする
import logging
logging.getLogger('matplotlib').setLevel(logging.ERROR)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from datetime import datetime

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, figure=None):
        # figure が渡されていない場合、空の Figure を作成
        if figure is None:
            figure = Figure()
        super(MplCanvas, self).__init__(figure)
        self.figure = figure
        self.axes1 = self.figure.add_subplot(111)
        self.axes2 = self.axes1.twinx()
        self.logger = logging.getLogger('__main__').getChild(__name__)
        self.clear()
        
    def clear(self):
        self.axes1.clear()
        self.axes2.clear()
        self.draw()
    
    def gen_graph(self, title, xlabel, ylabel1, ylabel2, dark_theme=False):
        self.title = title
        self.xlabel = xlabel
        self.ylabel1 = ylabel1
        self.ylabel2 = ylabel2
        
        # ダークテーマの設定
        if dark_theme:
            plt.style.use('dark_background')
            title_color = 'white'
            label_color = 'white'
            bg_color = '#323232'
            plt_color = 'black'
        else:
            title_color = 'black'
            label_color = 'black'
            bg_color = '#ECECEC'
            plt_color = 'white'
            
        self.figure.set_facecolor(bg_color)
        self.axes1.set_facecolor(plt_color)
        self.axes2.set_facecolor(plt_color)
        
        self.axes1.set_xlabel(xlabel, color=label_color)
        self.axes1.set_ylabel(ylabel1, color=label_color)
        
        self.axes1.tick_params(pad=10, color=label_color, labelcolor=label_color)
        self.axes2.tick_params(pad=10, color=label_color, labelcolor=label_color)
        
        self.line1, = self.axes1.plot([], [], marker='o', color='royalblue', label=ylabel1)
        self.line2, = self.axes2.plot([], [], marker='s', color='tomato', label=ylabel2)
        
        self.axes1.set_ylim(-0.1, 1.1)
        self.axes1.set_title(title, color=title_color)
        
        lines = [self.line1, self.line2]
        self.axes1.legend(lines, [line.get_label() for line in lines], loc='upper left')

        self.draw()

    def update_existing_plot(self, x_val, y_val1, y_val2):
        # 時間データを数値に変換
        x_val_datetime = [datetime.strptime(t, '%H:%M:%S') for t in x_val]
        x_val_num = mdates.date2num(x_val_datetime)
        
        self.line1.set_data(x_val_num, y_val1)
        self.line2.set_data(x_val_num, y_val2)

        self.axes1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
        # x軸の範囲設定
        if len(x_val_num) > 1:
            x_min, x_max = x_val_num[0], x_val_num[-1]
            x_margin = (x_max - x_min) * 0.05  # データの5%を余裕として設定
            self.axes1.set_xlim(x_min - x_margin, x_max + x_margin)

        self.axes2.relim()
        self.axes2.autoscale_view()
        
        # 表示するラベルの数を制限
        max_labels = 5
        step = max(1, len(x_val) // max_labels)
        ticks = x_val_num[::step]
        labels = [x_val[i] for i in range(0, len(x_val), step)]
        self.axes1.set_xticks(ticks)
        self.axes1.set_xticklabels(labels)

        self.figure.tight_layout()
        self.draw()
