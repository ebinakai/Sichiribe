from PyQt6.QtCore import pyqtSignal, QThread
from cores.exporter import Exporter
import logging

class ExportWorker(QThread):
    finished = pyqtSignal()

    def __init__(self, params):
        super().__init__()
        self.params = params
        self.ep = Exporter(params['format'], params['out_dir'])
        self.logger = logging.getLogger('__main__').getChild(__name__)

    def run(self):
        data = self.ep.format(self.params['results'], self.params['timestamps'])
        self.ep.export(data)
        
        self.finished.emit()
        self.params = None