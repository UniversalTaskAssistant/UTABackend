import os
import cv2
import json
import xmltodict
from os.path import join as pjoin


class UIData:
    def __init__(self, screenshot_file, xml_file=None,
                 ui_resize=(1080, 2280), output_dir='data/app1'):
        self.screenshot_file = screenshot_file
        self.xml_file = xml_file
        self.ui_no = screenshot_file.replace('/', '\\').split('\\')[-1].split('.')[0]

        # UI info
        self.ui_screenshot = cv2.resize(cv2.imread(screenshot_file), ui_resize)   # ui screenshot
        self.ui_xml_vh = xmltodict.parse(open(xml_file, 'r', encoding='utf-8').read())   # ui vh xml
        self.ui_json_vh = None  # ui vh json, after processing

        # UI elements
        self.elements = []          # list of element in dictionary {'id':, 'class':...}
        self.elements_leaves = []   # leaf nodes that does not have children
        self.element_tree = None    # structural element tree, dict type
        self.blocks = []            # list of blocks from element tree
        self.ocr_text = []          # UI ocr detection result, list of texts {}

        # output file paths
        self.output_dir = pjoin(output_dir, 'guidata')
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_file_path_elements = pjoin(self.output_dir, self.ui_no + '_elements.json')
        self.output_file_path_element_tree = pjoin(self.output_dir, self.ui_no + '_tree.json')
