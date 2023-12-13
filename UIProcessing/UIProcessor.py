import os
import cv2
import json
import xmltodict
from os.path import join as pjoin

from _UIData import _UIData
from _UIPreProcessor import _UIPreProcessor
from _UIAnalyser import _UIAnalyser


class UIProcessor:
    def __init__(self):
        self.ui_data = None
        self.ui_preprocessor = _UIPreProcessor()
        self.ui_analyser = _UIAnalyser()

    def process_ui(self, ui_data):

        return ui_info
