from uta.config import *
from uta.UIProcessing._UIPreProcessor import _UIPreProcessor
from uta.UIProcessing._UIAnalyser import _UIAnalyser


class UIProcessor:
    def __init__(self, model_manager):
        self.__model_manager = model_manager

        self.__ui_preprocessor = _UIPreProcessor()
        self.__ui_analyser = _UIAnalyser(self.__model_manager)

    def ui_vh_xml_cvt_to_json(self, ui_data):
        """
        Convert xml vh to json format for easier processing
        Args:
            ui_data (UIData): ui data for processing
        Returns:
            ui_data.ui_vh_json (dict): VH in a tidy json format
        """
        print('* Reformat xml vh *')
        self.__ui_preprocessor.ui_vh_xml_cvt_to_json(ui_data=ui_data)

    def ui_info_extraction(self, ui_data):
        """
        Extract elements from raw view hierarchy Json file and store them as dictionaries
        Args:
            ui_data (UIData): ui data for processing
        Returns:
            ui_data.elements; ui_data.elements_leaves (list of dicts)
        """
        print('* Extract ui elements from vh *')
        self.__ui_preprocessor.ui_info_extraction(ui_data=ui_data)

    def ui_analysis_elements_description(self, ui_data, ocr=True, cls=True):
        """
        Extract description for UI elements through 'text', 'content-desc', 'classification' and 'caption'
        Args:
            ui_data (UIData): Target UI data for analysis
            ocr (bool): True to turn on ocr for the whole UI image
            cls (bool): True to turn on UI element classification
        Returns:
            ui_data.element['description']: 'description' attribute in element
        """
        print('* Analyse descriptions for elements *')
        self.__ui_analyser.ui_analysis_elements_description(ui_data=ui_data, ocr=ocr, cls=cls)

    def ui_build_element_tree(self, ui_data):
        """
        Build a hierarchical element tree with a few key attributes to represent the vh
        Args:
            ui_data (UIData): Target UI data for analysis
        Returns:
            ui_data.element_tree (dict): structural element tree
        """
        print('* Organize simplified element tree *')
        self.__ui_analyser.ui_build_element_tree(ui_data)

    def process_ui(self, ui_data, show=False):
        """
        Process a UI, including
            1. Convert vh to tidy and formatted json
            2. Extract basic UI info (elements) and store as dicts
            3. Analyze UI element to attach description
            4. Build element tree based on the prev to represent the UI
        Args:
            ui_data (UIData): UI data before processing
            show (bool): True to show processing result on window
        Returns:
             ui_data (UIData): UI data after processing
        """
        print('\n *** Process UI ***')
        self.ui_vh_xml_cvt_to_json(ui_data)
        self.ui_info_extraction(ui_data)
        self.ui_analysis_elements_description(ui_data)
        self.ui_build_element_tree(ui_data)
        if show:
            ui_data.show_all_elements()
        return ui_data


if __name__ == '__main__':
    from uta.ModelManagement import ModelManager
    model_mg = ModelManager()
    model_mg.initialize_vision_model()

    ui = UIProcessor(model_manager=model_mg)
    uidata = ui.load_ui_data(screenshot_file=WORK_PATH + 'data/0.png', xml_file=WORK_PATH + 'data/0.xml', ui_resize=(1080, 1920))
    uidata = ui.process_ui(ui_data=uidata)