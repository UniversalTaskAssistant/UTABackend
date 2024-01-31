from os.path import join as pjoin
from testing.Device import Device
from uta.UTA import UTA
from uta.config import *

# set up user task
task = 'Send message to my mom'
user_id = 'user1'
task_id = 'task2'
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
while True:
    ui_img, ui_xml = device.cap_and_save_ui_screenshot_and_xml(ui_id=ui_id, output_dir=pjoin(DATA_PATH, user_id, task_id))
    package, activity = device.get_current_package_and_activity_name()
    keyboard_active = device.check_keyboard_active()
    ui_data, action = uta.automate_task(user_id=user_id, task_id=task_id, ui_img_file=ui_img, ui_xml_file=ui_xml,
                                        package_name=package, activity_name=activity, keyboard_active=keyboard_active, printlog=False)
    if 'complete' in action['Action'].lower():
        break
    device.take_action(action=action, ui_data=ui_data, show=True)
    ui_id += 1
