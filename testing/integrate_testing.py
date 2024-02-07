from os.path import join as pjoin
import os
import cv2
import json
import traceback
import time

from testing.Device import Device
from testing.data_util import *
from uta.UTA import UTA
from uta.config import *
from uta.SystemConnection import SystemConnector


def annotate_ui_operation(ui, recommended_action):
    """
    Create annotated UI for debugging
    """
    assert recommended_action != "None"

    try:
        ele = ui.elements[int(recommended_action["Element Id"])]
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

            if dec.get("Action") is not None and dec["Action"] == "Error at the backend.":
                save_error(dec["Exception"], dec["Traceback"], "declaration_error")
                break

            if dec['Proc'] == 'Clarify':
                print(dec)
                msg = input('Input your answer:')
            else:
                break
        except Exception as e:
            print(e)
            error_trace = traceback.format_exc()  # Get the stack trace
            save_error(e, error_trace, "declaration_error")
            break


def task_automation(max_try=20):
    ui_id = 0
    for i in range(max_try):
        try:
            ui_img, ui_xml = device.cap_and_save_ui_screenshot_and_xml(ui_id=ui_id,
                                                                       output_dir=pjoin(DATA_PATH, user_id, task_id))
            package, activity = device.get_current_package_and_activity_name()
            keyboard_active = device.check_keyboard_active()
            ui_data, action = uta.automate_task(user_id=user_id, task_id=task_id, ui_img_file=ui_img,
                                                ui_xml_file=ui_xml,
                                                package_name=package, activity_name=activity,
                                                keyboard_active=keyboard_active, printlog=False)

            # ui_path = pjoin(DATA_PATH, user_id, task_id)
            # ui_tree = SystemConnector().load_json(pjoin(ui_path, f"{i}_uitree.json"))
            # ui_data = SystemConnector().load_ui_data(pjoin(ui_path, f"{i}.png"), pjoin(ui_path, f"{i}.xml"), resolution)
            # ui_data.elements = ui_tree

            if action.get("Action") is not None and "error" in action["Action"].lower():
                save_error(action["Exception"], action["Traceback"], "automation_error")
                break

            annotate_screenshot = annotate_ui_operation(ui_data, action)
            screen_path = pjoin(DATA_PATH, user_id, task_id, f"{ui_id}_annotated.png")
            SystemConnector().save_img(annotate_screenshot, screen_path)
            # with open(screen_path, 'wb') as fp:
            #     fp.write(annotate_screenshot)

            if 'complete' in action['Action'].lower():
                break
            device.take_action(action=action, ui_data=ui_data, show=False)
            time.sleep(2)  # wait the action to be done
            ui_id += 1
        except Exception as e:
            print(e)
            error_trace = traceback.format_exc()  # Get the stack trace
            save_error(e, error_trace, "automation_error")
            break


def save_error(e, error_trace, save_name):
    error_json = {
        'error': str(e),
        'traceback': error_trace  # Save the stack trace in the JSON
    }
    task_folder = pjoin(DATA_PATH, user_id, task_id)
    if not os.path.exists(task_folder):
        os.makedirs(task_folder)
    error_path = pjoin(task_folder, f"{save_name}.json")
    SystemConnector().save_json(error_json, error_path)
    # with open(error_path, "w", encoding='utf-8') as fp:
    #     json.dump(error_json, fp, indent=4)


# set up user task
user_id = 'user4_5'
# init device
device = Device()
device.connect()

resolution = device.get_device_resolution()
# init uta
uta = UTA()
uta.setup_user(user_id=user_id, device_resolution=resolution, app_list=app_list)

for task_idx, task in enumerate(task_list):
    # if task_idx not in [0, 9, 13, 21, 24, 25, 26, 27, 28, 35, 37, 38, 41, 42, 43, 44, 45, 46, 47, 48, 51, 53, 54, 55,
    #                     56, 57, 58, 59, 60, 61, 62, 64, 65, 66, 72, 81, 82, 83, 85, 86, 87, 89, 92, 93, 95]:
    #     continue
    if task_idx not in [0, 9, 13]:
        continue
    # if task_idx < 5:
    #     continue
    # if not 80 < task_idx <= 90:
    #     continue
    task_id = f"task{task_idx + 1}"

    # task declaration
    # task_declaration(task, max_try=10)

    # task automation
    device.go_homepage()
    user, task_obj = uta.instantiate_user_task(user_id, task_id)
    device.reboot_app(task_obj.involved_app_package)
    task_automation(max_try=20)

device.disconnect()
