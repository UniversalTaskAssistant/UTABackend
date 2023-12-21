from DataStructures.config import *

test_section = 3

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
    ui_data = ui.process_ui(ui_data=ui_data, show=True)

    # save result to local
    from SystemConnection import SystemConnector
    system_connector = SystemConnector()
    system_connector.save_json(ui_data.elements, ui_data.output_file_path_elements)
    system_connector.save_json(ui_data.element_tree, ui_data.output_file_path_element_tree)

elif test_section == 2:
    '''
    ************************************
    *** Section 2 - Task Declaration ***
    ************************************
    '''
    # initiate model manager
    from ModelManagement import ModelManager
    model_mg = ModelManager()

    # declare task
    from TaskDeclearation.TaskDeclaration import TaskDeclarator
    task = 'Open wechat and send my mom a message'
    task_declarator = TaskDeclarator(model_manager=model_mg)
    task_declarator.initialize_task_clarifier('task_clarifier1')
    task_declarator.clarify_task(clarifier_identifier='task_clarifier1', org_task=task)
    task_declarator.initialize_task_decomposer('task_dec1')
    task_declarator.decompose_task(decomposer_identifier='task_dec1', task=task)
    task_declarator.initialize_task_classifier('task_cls1')
    task_declarator.classify_task(classifier_identifier='task_cls1', task=task)

elif test_section == 3:
    '''
    **********************************
    *** Section 3 - Task Execution ***
    **********************************
    '''
    # initiate model manager
    from ModelManagement import ModelManager
    model_manager = ModelManager()
    model_manager.initialize_llm_model(identifier='ui_relation_checker')
    model_manager.initialize_llm_model(identifier='ui_action_checker')

    # load testing ui
    from SystemConnection import SystemConnector
    from DataStructures import UIData
    system_connector = SystemConnector()
    ui_data = UIData('./data/device/1.png')
    ui_data.elements = system_connector.load_json('./data/ui/1_elements.json')
    ui_data.element_tree = system_connector.load_json('./data/ui/1_tree.json')

    # check ui action
    from TaskExecution import AppTasker
    task = 'Open the youtube'
    app_tasker = AppTasker(model_manager=model_manager, ui_relation_checker_identifier='ui_relation_checker', ui_action_checker_identifier='ui_action_checker')
    app_tasker.check_task_ui_relation(ui_data, task)
    app_tasker.check_ui_action(ui_data, task)
    app_tasker.analyze_ui_task(ui_data, task)

elif test_section == 4:
    '''
    ***********************************
    *** Section 4 - Third Party App ***
    ***********************************
    '''
    # initiate model manager
    from ModelManagement import ModelManager
    model_mg = ModelManager()

    # check third party apps
    from ThirdPartyAppManagement import ThirdPartyAppManager
    app_mg = ThirdPartyAppManager(model_manager=model_mg)
    apps = app_mg.search_apps_fuzzy('chinese food')
