import cv2
import time

from uta.DataStructures import *
from uta.ModelManagement import ModelManager
from uta.ModelManagement.FMModel import _OpenAI
from uta.ModelManagement.VisionModel import _GoogleOCR, _IconClassifier

from uta.SystemConnection import _Local, SystemConnector
from uta.UIProcessing import UIProcessor
from uta.TaskDeclearation import TaskDeclarator
from testing.Device import Device

from uta.ThirdPartyAppManagement import ThirdPartyAppManager, _GooglePlay
from uta.TaskAction import _TaskUIChecker, TaskActionChecker

from uta.config import *


def test_task():
    task = Task("1", "1", "Open Youtube")
    print(task)
    print(task.to_dict())

    new_task = {'task_id': "2", "user_id": "2", "task_description": "Close Youtube", "fake_attr": "abc"}
    task.load_from_dict(new_task)
    print(task.to_dict())

    action = {"Action": "Long Press", "Element": "19", "Description": "N/A", "Input Text": "N/A", "Reason": "N/A"}
    task.actions.append(action)
    print(task.to_dict())


def test_llmmodel():
    llm_model = _OpenAI()
    conversation = []
    while True:
        user_input = input()
        user_input = {'role': 'user', 'content': user_input}
        conversation.append(user_input)
        msg = llm_model.send_openai_conversation(conversation, printlog=True, runtime=True)
        print(msg)
        conversation.append(msg)


def test_googleocr():
    img_path = WORK_PATH + 'old_test_data/test/general/0.png'
    google_ocr = _GoogleOCR()
    img_data2 = google_ocr.detect_text_ocr(img_path, output_dir=WORK_PATH + 'old_test_data/test/output/',
                                           show=True, shrink_size=True)
    print(img_data2)


def test_iconclassifier():
    img_path = WORK_PATH + 'old_test_data/test/classification/a1.jpg'
    icon_classifier = _IconClassifier()
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = icon_classifier.classify_icons([img_rgb])
    print("Classification Result:", result)


def test_model_manager():
    model_manager = ModelManager()
    # conversation = []
    # for i in range(2):
    #     user_input = input()
    #     user_input = {'role': 'user', 'content': user_input}
    #     conversation.append(user_input)
    #     msg = model_manager.send_fm_conversation(conversation, printlog=True, runtime=True)
    #     print(msg)
    #     conversation.append(msg)

    # img_path = WORK_PATH + 'old_test_data/test/general/0.png'
    # img_data2 = model_manager.detect_text_ocr(img_path)
    # print(img_data2)

    # img_path = WORK_PATH + 'old_test_data/test/classification/a1.jpg'
    # img = cv2.imread(img_path)
    # img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # result = model_manager.classify_icons([img_rgb])
    # print("Classification Result:", result)

    token_counts = model_manager.count_token_size("I like apple.")
    print(token_counts)


def test_local():
    img_path = WORK_PATH + 'old_test_data/test/general/0.png'
    xml_path = WORK_PATH + 'old_test_data/test/general/0.xml'
    json_path = WORK_PATH + 'old_test_data/1/I want to see a youtube introducing canberra raiders, ' \
                                    'if there is any advertisement in the ' \
                                    'middle of playing, and it is skipable,please help me skip it/device/1.json'

    img_write_path = WORK_PATH + 'old_test_data/test/local/0.png'
    xml_write_path = WORK_PATH + 'old_test_data/test/local/0.xml'
    json_write_path = WORK_PATH + 'old_test_data/test/local/1.json'

    img = _Local().load_img(img_path)
    xml_file = _Local().load_xml(xml_path)
    json_file = _Local().load_json(json_path)

    print(img)
    print(xml_file)
    print(json_file)

    _Local().save_img(img, img_write_path)
    _Local().save_xml(xml_file, xml_write_path)
    _Local().save_json(json_file, json_write_path)
    print(1)


def test_systemcomnnector():
    system_connector = SystemConnector()
    user = system_connector.load_user("user1")
    task = system_connector.load_task("user1", "task1")

    screenshot = DATA_PATH + 'user1/task1/0.png'
    xml_file = DATA_PATH + 'user1/task1/0.xml'
    ui_data = system_connector.load_ui_data(screenshot_file=screenshot, xml_file=xml_file)

    print(user.to_dict())
    print(task.to_dict())
    print(ui_data.to_dict())

    system_connector.save_task(task)
    system_connector.save_user(user)
    system_connector.save_ui_data(ui_data, DATA_PATH + 'user1/task1/')


def test_uiprocessor():
    model_manager = ModelManager()
    ui_processor = UIProcessor(model_manager)

    screenshot = DATA_PATH + 'user1/task1/0.png'
    xml_file = DATA_PATH + 'user1/task1/0.xml'
    ui_data = UIData(screenshot_file=screenshot, xml_file=xml_file)
    print(ui_data.to_dict())

    new_ui = ui_processor.process_ui(ui_data=ui_data, show=True)
    new_ui.annotate_ui_operation({"Action": "Click", "Coordinate": 3, "Element": "3", "others": "N/A"})
    print(new_ui.to_dict())

    board = new_ui.annotated_screenshot
    cv2.imshow('long_press', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
    cv2.waitKey()
    cv2.destroyWindow('long_press')


def test_task_declarator():
    model_manager = ModelManager()
    task_declarator = TaskDeclarator(model_manager)
    description = "I want to watch football videos"
    # description = "How are you today?"
    task = Task("1", "1", description)
    print(task.to_dict())

    resp = task_declarator.clarify_task(task, printlog=True)
    print(task.to_dict())
    resp = task_declarator.classify_task(task)
    print(task.to_dict())
    resp = task_declarator.decompose_task(task)
    print(task.to_dict())
    # print(resp)


def test_googleplay():
    google_play = _GooglePlay()
    print(google_play.search_app_by_name('youtube'))
    print(google_play.search_apps_fuzzy('youtube'))


def test_appmanager():
    model_manager = ModelManager()
    app_manager = ThirdPartyAppManager(model_manager)

    app_list = ['com.google.android.apps.youtube YouTube',
                'com.google.android.apps.youtube.kids YouTube Kids',
                'com.google.android.apps.youtube.unplugged YouTube TV: Live TV & more',
                'com.google.android.apps.youtube.music YouTube Music',
                'com.google.android.youtube.tv YouTube for Android TV',
                'com.google.android.youtube.tvunplugged YouTube TV: Live TV & more',
                'com.google.android.apps.youtube.creator YouTube Studio',
                'com.google.android.apps.youtube.music.pwa YouTube Music for Chromebook',
                'com.google.android.youtube.tvkids YouTube Kids for Android TV',
                'com.google.android.youtube.tvmusic YouTube Music',
                'com.google.android.videos Google TV',
                'com.netflix.mediaclient Netflix',
                'com.tubitv Tubi: Movies & Live TV',
                'com.amazon.avod.thirdpartyclient Amazon Prime Video',
                'com.google.android.apps.youtube.producer YouTube Create',
                'com.disney.disneyplus Disney+',
                'com.vimeo.android.videoapp Vimeo',
                'com.crunchyroll.crunchyroid Crunchyroll',
                'com.hulu.plus Hulu: Stream TV shows & movies',
                'com.plexapp.android Plex: Stream Movies & TV']
    task = Task("1", "1", "I want to watch a football match with my mobile.")
    res = app_manager.check_related_apps(task, app_list, printlog=True)
    print(res)


def test_device():
    device = Device()
    # print(device.is_connected())
    # device.connect()
    # print(device.is_connected())
    # device.disconnect()
    # print(device.is_connected())
    device.connect()

    # wm = device.get_device_resolution()
    # print(wm)

    # print(device.get_app_list_on_the_device())
    # device.launch_app('com.google.android.youtube')
    # print(device.get_current_package_and_activity_name())
    # print(device.get_device())
    # print(device.get_device_name())
    # print(device.check_keyboard_active())
    # device.go_back()
    # device.close_app('com.google.android.youtube')

    # img_write_path = WORK_PATH + 'old_test_data/test/guidata/1.png'
    # screen = device.cap_screenshot()
    # _Local().save_img(screen, img_write_path)
    # print(device.cap_current_ui_hierarchy_xml())
    # screen_path, xml_path = device.cap_and_save_ui_screenshot_and_xml("2", WORK_PATH + 'old_test_data/test/guidata/')
    # print(screen_path, xml_path)

    elements = _Local().load_json(WORK_PATH + 'old_test_data/test/guidata/0_elements.json')
    tree = _Local().load_json(WORK_PATH + 'old_test_data/test/guidata/0_tree.json')
    system_connector = SystemConnector()
    screenshot = WORK_PATH + 'old_test_data/test/guidata/0.png'
    xml_file = WORK_PATH + 'old_test_data/test/guidata/0.xml'
    gui = system_connector.load_ui_data(screenshot_file=screenshot, xml_file=xml_file)
    gui.elements = elements
    gui.element_tree = tree

    # device.right_swipe_screen(gui, 0, True)
    # device.left_swipe_screen(gui, 0, True)
    # device.up_scroll_screen(gui, 0, True)
    # device.down_scroll_screen(gui, 0, True)
    # device.long_press_screen(gui, 19, True)
    # device.click_screen(gui, 19, True)

    # for act in ["Swipe", "Scroll", "Click", "Launch"]:
    #     cood = 0 if act != "Click" else 19
    #     action = {"Action": act, "Coordinate": cood, "Element": str(cood), "App": 'com.google.android.youtube',
    #               "Input Text": "something."}
    #     device.take_action(action, ui_data=gui, show=False)
    #     time.sleep(3)

    # test input independently
    cood = 19
    act = "Input"
    action = {"Action": act, "Coordinate": cood, "Element": str(cood), "App": 'com.google.android.youtube',
              "Input Text": "something."}
    device.take_action(action, ui_data=gui, show=True)


def test_taskuichecker():
    model_manager = ModelManager()
    task_ui_checker = _TaskUIChecker(model_manager)

    elements = _Local().load_json(WORK_PATH + 'old_test_data/test/guidata/0_elements.json')
    tree = _Local().load_json(WORK_PATH + 'old_test_data/test/guidata/0_tree.json')
    system_connector = SystemConnector()
    screenshot = WORK_PATH + 'old_test_data/test/guidata/0.png'
    xml_file = WORK_PATH + 'old_test_data/test/guidata/0.xml'
    wm = (1080, 2400)
    gui = system_connector.load_ui_data(screenshot_file=screenshot, xml_file=xml_file, ui_resize=wm)
    gui.elements = elements
    gui.element_tree = tree

    task = Task("1", "1", 'Open the youtube')

    task_declarator = TaskDeclarator(model_manager)
    task_declarator.clarify_task(task, printlog=True)
    task_declarator.classify_task(task)
    task_declarator.decompose_task(task)

    new_prompt = task_ui_checker.wrap_task_info(task)
    print(new_prompt)

    res = task_ui_checker.check_ui_relation(gui, task, printlog=True)
    print(task.to_dict())
    print(res)

    res = task_ui_checker.check_ui_relation(gui, task, printlog=True)
    print(task.to_dict())
    print(res)

    res = task_ui_checker.check_element_action(gui, task, printlog=True)
    print(task.to_dict())
    print(res)
    task = Task("1", "2", 'Go to the phone camera')
    res = task_ui_checker.check_ui_go_back_availability(gui, task, printlog=True)
    print(task.to_dict())
    print(res)


if __name__ == '__main__':
    # test_task()

    # test_llmmodel()
    # test_googleocr()
    # test_iconclassifier()
    # test_model_manager()

    # test_local()
    # test_systemcomnnector()
    # test_uiprocessor()
    # test_task_declarator()

    # test_googleplay()
    # test_appmanager()

    # test_device()
    test_taskuichecker()