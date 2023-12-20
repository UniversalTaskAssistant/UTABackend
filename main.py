# cap ui raw data on the emulator
from SystemConnection import _Device
device = _Device()
device.connect()
screen_path, xml_path = device.cap_and_save_ui_screenshot_and_xml(1, 'data/device')

# initiate model manager
from ModelManagement import ModelManager
model_mg = ModelManager()
model_mg.initialize_vision_model()

# process ui data
from UIProcessing.UIProcessor import UIProcessor
ui = UIProcessor(model_manager=model_mg)
ui_data = ui.load_ui_data(screenshot_file=screen_path, xml_file=xml_path, ui_resize=device.get_device_resolution())
ui.process_ui()
ui_data.show_all_elements()
