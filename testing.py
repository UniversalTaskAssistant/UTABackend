from DataStructures.config import *

test_section = 1

if test_section == 1:
    '''
    ***********************************************
    *** Section 1 - UI Acquiring and Processing ***
    ***********************************************
    '''
    # cap ui raw data on the emulator
    from SystemConnection import SystemConnector
    sys_connector = SystemConnector()
    sys_connector.connect_adb_device()
    screen_path, xml_path = sys_connector.cap_and_save_ui_screenshot_and_xml(ui_id=1, output_dir=WORK_PATH + 'data/device')

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

elif test_section == 2:
    '''
    ************************************
    *** Section 2 - Task Declaration ***
    ************************************
    '''
    from ModelManagement import ModelManager
    model_mg = ModelManager()
    model_mg.initialize_llm_model(identifier='task_decomposer')

    from TaskDeclearation.TaskDeclaration import TaskDeclarator
    task = 'Open wechat and send my mom a message'
    task_declarator = TaskDeclarator(model_manager=model_mg)
    task_declarator.initialize_task_clarifier('task_clarifier1')
    task_declarator.clarify_task(clarifier_identifier='task_clarifier1', org_task=task)
    task_declarator.initialize_task_decomposer('task_dec1')
    task_declarator.decompose_task(decomposer_identifier='task_dec1', task=task)
    task_declarator.initialize_task_classifier('task_cls1')
    task_declarator.classify_task(classifier_identifier='task_cls1', task=task)
