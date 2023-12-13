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

    def load_ui_data(self, screenshot_file, xml_file=None, ui_resize=(1080, 2280), output_dir='data/app1'):
        '''
        Load UI to UIData
        Args:
            screenshot_file (path): Path to screenshot image
            xml_file (path): Path to xml file if any
            ui_resize (tuple): Specify the size/resolution of the UI
            output_dir (path): Directory to store all processing result for the UI
        Returns:
            self.ui_data (UIData)
        '''
        self.ui_data = _UIData(screenshot_file, xml_file, ui_resize, output_dir)

    def process_ui(self, ui_data=None):
        '''
        Process a UI, including
            1. Convert vh to tidy and formatted json
            2. Extract basic UI info (elements) and store as dicts
            3. Analyze UI element to attach description
            4. Build element tree based on the prev to represent the UI
        Args:
            ui_data (UIData): UI data before processing
        Returns:
             ui_data (UIData): UI data after processing
        '''
        if not ui_data:
            ui_data = self.ui_data
        else:
            self.ui_data = ui_data
        self.ui_preprocessor.ui_vh_xml_cvt_to_json(ui_data)
        self.ui_preprocessor.ui_info_extraction(ui_data)
        self.ui_analyser.ui_analysis_elements_description(ui_data)
        self.ui_analyser.ui_build_element_tree(ui_data)
        ui_data.show_all_elements()
