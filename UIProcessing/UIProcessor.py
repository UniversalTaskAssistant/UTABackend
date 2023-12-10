import os
import cv2
import json
import xmltodict
from os.path import join as pjoin

from _UIData import UIData
from _UIPreProcessor import UIPreProcessor
from _UIAnalyser import UIAnalyser


class UIProcessor:
    def __init__(self):
        self.ui_data = None
        self.ui_preprocessor = None
        self.ui_analyser = None

    def process_ui(self, ui_img, ui_xml):
        return ui_info
