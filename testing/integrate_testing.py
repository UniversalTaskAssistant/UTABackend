from os.path import join as pjoin
import cv2
import json

from testing.Device import Device
from uta.UTA import UTA
from uta.config import *


def annotate_ui_operation(ui, recommended_action):
    """
    Create annotated UI for debugging
    """
    assert recommended_action != "None"

    try:
        ele = ui.elements[int(recommended_action["Element"])]
        bounds = ele['bounds']
        action_type = recommended_action['Action'].lower()

        if 'click' in action_type:
            centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
            board = ui.ui_screenshot.copy()
            cv2.circle(board, (centroid[0], centroid[1]), 20, (255, 0, 255), 8)
            annotated_screenshot = board
        elif 'press' in action_type:
            centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
            board = ui.ui_screenshot.copy()
            cv2.circle(board, (centroid[0], centroid[1]), 20, (255, 0, 255), 8)
            annotated_screenshot = board
        # elif 'scroll up' in action_type:
        #     scroll_start = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
        #     scroll_end = ((bounds[2] + bounds[0]) // 2, bounds[1])
        #     board = ui.ui_screenshot.copy()
        #     cv2.circle(board, scroll_start, 20, (255, 0, 255), 8)
        #     cv2.circle(board, scroll_end, 20, (255, 0, 255), 8)
        #     annotated_screenshot = board
        elif 'scroll' in action_type:
            scroll_end = ((bounds[2] + bounds[0]) // 2, bounds[3])
            scroll_start = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
            board = ui.ui_screenshot.copy()
            cv2.circle(board, scroll_start, 20, (255, 0, 255), 8)
            cv2.circle(board, scroll_end, 20, (255, 0, 255), 8)
            annotated_screenshot = board
        # elif 'swipe right' in action_type:
        #     bias = 20
        #     swipe_start = (bounds[0] + bias, (bounds[3] + bounds[1]) // 2)
        #     swipe_end = (bounds[2], (bounds[3] + bounds[1]) // 2)
        #     board = ui.ui_screenshot.copy()
        #     cv2.arrowedLine(board, swipe_start, swipe_end, (255, 0, 255), 8)
        #     annotated_screenshot = board
        elif 'swipe' in action_type:
            bias = 20
            swipe_start = (bounds[2] - bias, (bounds[3] + bounds[1]) // 2)
            swipe_end = (bounds[0], (bounds[3] + bounds[1]) // 2)
            board = ui.ui_screenshot.copy()
            cv2.arrowedLine(board, swipe_start, swipe_end, (255, 0, 255), 8)
            annotated_screenshot = board
        elif 'input' in action_type:
            text = recommended_action['Input Text']
            text_x = bounds[0] + 5  # Slightly right from the left bound
            text_y = (bounds[1] + bounds[3]) // 2  # Vertically centered
            board = ui.ui_screenshot.copy()
            cv2.putText(board, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            annotated_screenshot = board
        else:
            annotated_screenshot = ui.ui_screenshot.copy()
    except Exception as e:
        print(e)
        annotated_screenshot = ui.ui_screenshot.copy()
    _, encoded_image = cv2.imencode('.png', annotated_screenshot)
    return encoded_image.tobytes()
        
        
# set up user task
task = 'Open Youtube app for me'
user_id = 'user1'
task_id = 'task1'
# init device
device = Device()
device.connect()
app_list = device.get_app_list_on_the_device()
resolution = device.get_device_resolution()
# init uta
uta = UTA()
uta.setup_user(user_id=user_id, device_resolution=resolution, app_list=app_list)

# task declaration
msg = task
while True:
    dec = uta.declare_task(user_id=user_id, task_id=task_id, user_msg=msg)
    if dec['Proc'] == 'Clarify':
        print(dec['Question'], '\n', dec['Options'])
        msg = input('Input your answer:')
    else:
        break

# task automation
ui_id = 0
max_try = 20
for i in range(max_try):
    try:
        ui_img, ui_xml = device.cap_and_save_ui_screenshot_and_xml(ui_id=ui_id, output_dir=pjoin(DATA_PATH, user_id, task_id))
        package, activity = device.get_current_package_and_activity_name()
        keyboard_active = device.check_keyboard_active()
        ui_data, action = uta.automate_task(user_id=user_id, task_id=task_id, ui_img_file=ui_img, ui_xml_file=ui_xml,
                                            package_name=package, activity_name=activity, keyboard_active=keyboard_active, printlog=False)

        annotate_screenshot = annotate_ui_operation(ui_data, action)
        screen_path = pjoin(DATA_PATH, user_id, task_id, f"{str(ui_id)}_annotated.png")
        with open(screen_path, 'wb') as fp:
            fp.write(annotate_screenshot)

        if 'complete' in action['Action'].lower():
            break
        device.take_action(action=action, ui_data=ui_data, show=False)
        ui_id += 1
    except Exception as e:
        error_json = {'error': str(e)}
        error_path = pjoin(DATA_PATH, user_id, task_id, f"error.json")
        with open(error_path, "w", encoding='utf-8') as fp:
            json.dump(error_json, fp, indent=4)