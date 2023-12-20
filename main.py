from DataStructures.config import *

# cap ui raw data on the emulator
from SystemConnection import SystemConnector
sys_connector = SystemConnector()
sys_connector.connect_adb_device()
screen_path, xml_path = sys_connector.cap_and_save_ui_screenshot_and_xml(1, WORK_PATH + 'data/device')

# initiate model manager
from ModelManagement import ModelManager
model_mg = ModelManager()
model_mg.initialize_vision_model()

# process ui data
from UIProcessing.UIProcessor import UIProcessor
ui = UIProcessor(model_manager=model_mg)
ui_data = ui.load_ui_data(screenshot_file=screen_path, xml_file=xml_path, ui_resize=sys_connector.get_device_resolution())
ui.process_ui()
ui_data.show_all_elements()
