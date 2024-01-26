from os.path import join as pjoin
import cv2
import json
import traceback
import time

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


def task_declaration(msg, max_try=20):
    for i in range(max_try):
        try:
            dec = uta.declare_task(user_id=user_id, task_id=task_id, user_msg=msg)
            if dec['Proc'] == 'Clarify':
                print(dec['Question'], '\n', dec['Options'])
                msg = input('Input your answer:')
            else:
                break
        except Exception as e:
            print(e)
            error_trace = traceback.format_exc()  # Get the stack trace
            error_json = {
                'error': str(e),
                'traceback': error_trace  # Save the stack trace in the JSON
            }
            error_path = pjoin(DATA_PATH, user_id, task_id, f"declaration_error.json")
            with open(error_path, "w", encoding='utf-8') as fp:
                json.dump(error_json, fp, indent=4)
            break


def task_automation(max_try=20):
    ui_id = 0
    for i in range(max_try):
        try:
            ui_img, ui_xml = device.cap_and_save_ui_screenshot_and_xml(ui_id=ui_id, output_dir=pjoin(DATA_PATH, user_id, task_id))
            package, activity = device.get_current_package_and_activity_name()
            keyboard_active = device.check_keyboard_active()
            ui_data, action = uta.automate_task(user_id=user_id, task_id=task_id, ui_img_file=ui_img, ui_xml_file=ui_xml,
                                                package_name=package, activity_name=activity, keyboard_active=keyboard_active, printlog=False)

            annotate_screenshot = annotate_ui_operation(ui_data, action)
            screen_path = pjoin(DATA_PATH, user_id, task_id, f"{ui_id}_annotated.png")
            with open(screen_path, 'wb') as fp:
                fp.write(annotate_screenshot)

            if 'complete' in action['Action'].lower():
                break
            device.take_action(action=action, ui_data=ui_data, show=False)
            time.sleep(2)  # wait the action to be done
            ui_id += 1
        except Exception as e:
            print(e)
            error_trace = traceback.format_exc()  # Get the stack trace
            error_json = {
                'error': str(e),
                'traceback': error_trace  # Save the stack trace in the JSON
            }
            error_path = pjoin(DATA_PATH, user_id, task_id, f"automation_error.json")
            with open(error_path, "w", encoding='utf-8') as fp:
                json.dump(error_json, fp, indent=4)
            break


# set up user task
user_id = 'user1'
# init device
device = Device()
device.connect()
app_list = device.get_app_list_on_the_device()
resolution = device.get_device_resolution()
# init uta
uta = UTA()
uta.setup_user(user_id=user_id, device_resolution=resolution, app_list=app_list)

task_list = ['Open Language Setting page of my mobile', 'Open Youtube app for me', 'I want to enlarge the font size of my phone',
             'I want to boost volume', 'I want to open auto-read function',
             'I want to add a contact number, the name is Mulong Xie and phone number is 0450674929',
             'I want to set a special ringtone for the call of my friend Mulong',
             'I want to listen radio about world news',
             'I want to take a photo', 'I want to edit the last photo and add text "hello" in it',
             'I want to open my bluetooth', 'I want to look at my album', 'tell me today\'s weather',
             ' I want to open my wifi', 'I need to open my hotspot',
             'I want to set Mulong as a quick-dial number, there should be a icon on the screen that I can directly call him by pressing it',
             'I want to take note "I like apple", and I want the phone use sound to read it for me',
             'I want to translate the "I like apple" into French', 'I need to go to the nearest market',
             'I want to see a youtube introducing canberra raiders', 'please tell me what time it is now in voice',
             'Can you help me clean my phone\'s memory?',
             'I want to cook a pasta for my son, I totally have no idea']

for task_idx, task in enumerate(task_list):
    if task_idx != 21:
        continue
    task_id = f"task{task_idx+1}"
    # go homepage
    device.go_homepage()

    # task declaration
    # task_declaration(task)

    # task automation
    task_automation(max_try=10)
