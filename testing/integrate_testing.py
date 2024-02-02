from os.path import join as pjoin
import os
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

            if dec.get("Action") is not None and dec["Action"] == "Error at the backend.":
                save_error(dec["Exception"], dec["Traceback"], "declaration_error")
                break

            if dec['Proc'] == 'Clarify':
                print(dec['Question'], '\n', dec['Options'])
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
            ui_img, ui_xml = device.cap_and_save_ui_screenshot_and_xml(ui_id=ui_id, output_dir=pjoin(DATA_PATH, user_id, task_id))
            package, activity = device.get_current_package_and_activity_name()
            keyboard_active = device.check_keyboard_active()
            ui_data, action = uta.automate_task(user_id=user_id, task_id=task_id, ui_img_file=ui_img, ui_xml_file=ui_xml,
                                                package_name=package, activity_name=activity, keyboard_active=keyboard_active, printlog=False)

            if action.get("Action") is not None and "error" in action["Action"].lower():
                save_error(action["Exception"], action["Traceback"], "automation_error")
                break

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
    with open(error_path, "w", encoding='utf-8') as fp:
        json.dump(error_json, fp, indent=4)


# set up user task
user_id = 'user3'
# init device
device = Device()
device.connect()
# app_list = device.get_app_list_on_the_device()
# rest is for API34
# app_list = ['com.android.systemui.auto_generated_rro_vendor__', 'com.google.android.providers.media.module', 'com.google.android.overlay.permissioncontroller', 'com.google.android.overlay.googlewebview', 'com.android.calllogbackup', 'com.android.carrierconfig.auto_generated_rro_vendor__', 'com.android.systemui.accessibility.accessibilitymenu', 'com.android.internal.emulation.pixel_3_xl', 'com.android.providers.contacts', 'com.android.internal.emulation.pixel_4a', 'com.android.dreams.basic', 'com.android.companiondevicemanager', 'com.android.cts.priv.ctsshim', 'com.google.android.calendar', 'com.google.android.networkstack.tethering.emulator', 'com.google.android.contacts', 'com.android.mms.service', 'com.google.android.cellbroadcastreceiver', 'com.android.providers.downloads', 'com.android.bluetoothmidiservice', 'com.android.credentialmanager', 'com.google.android.printservice.recommendation', 'com.google.android.captiveportallogin', 'com.android.storagemanager.auto_generated_rro_product__', 'com.google.android.networkstack', 'com.google.android.overlay.googleconfig', 'com.android.keychain', 'com.google.android.tag', 'com.android.internal.emulation.pixel_2_xl', 'android.auto_generated_rro_vendor__', 'com.google.android.apps.wellbeing', 'com.android.nfc.auto_generated_rro_product__', 'com.android.virtualmachine.res', 'com.android.emulator.multidisplay', 'com.android.shell', 'com.google.android.adservices.api', 'com.google.android.wifi.dialog', 'com.google.android.apps.wallpaper.nexus', 'com.android.inputdevices', 'com.google.android.ondevicepersonalization.services', 'com.google.android.apps.customization.pixel', 'com.android.bookmarkprovider', 'com.google.android.onetimeinitializer', 'com.google.android.permissioncontroller', 'com.google.android.overlay.largescreenconfig', 'com.android.internal.emulation.pixel_6a', 'com.android.sharedstoragebackup', 'com.android.imsserviceentitlement', 'com.android.providers.media', 'com.android.providers.calendar', 'com.android.providers.blockednumber', 'com.google.android.documentsui', 'com.google.android.googlesdksetup', 'com.android.carrierconfig.auto_generated_rro_product__', 'com.google.android.devicelockcontroller', 'com.android.proxyhandler', 'com.android.systemui.emulation.pixel_3a', 'com.android.emergency.auto_generated_rro_product__', 'com.android.managedprovisioning', 'com.android.emergency', 'com.google.android.telephony.satellite', 'com.android.managedprovisioning.auto_generated_rro_product__', 'com.google.android.gm', 'com.android.carrierdefaultapp', 'com.android.backupconfirm', 'com.google.android.hotspot2.osulogin', 'com.android.nfc', 'com.google.android.deskclock', 'com.android.mtp', 'com.android.systemui.emulation.pixel_4a', 'com.google.android.gsf', 'com.google.android.overlay.pixelconfigcommon', 'com.android.internal.display.cutout.emulation.double', 'com.android.theme.font.notoserifsource', 'com.android.traceur.auto_generated_rro_product__', 'com.google.android.health.connect.backuprestore', 'com.google.android.settings.intelligence', 'com.android.systemui.emulation.pixel_3', 'com.android.systemui', 'com.android.wallpapercropper', 'com.android.internal.emulation.pixel_4', 'com.android.systemui.emulation.pixel_7', 'com.android.internal.emulation.pixel_fold', 'com.android.internal.emulation.pixel_5', 'com.android.systemui.emulation.pixel_6', 'com.android.providers.contacts.auto_generated_rro_product__', 'com.google.android.dialer', 'com.android.systemui.emulation.pixel_5', 'com.android.internal.emulation.pixel_3', 'com.android.systemui.emulation.pixel_4', 'com.android.internal.emulation.pixel_6', 'com.android.internal.systemui.navbar.gestural', 'com.android.internal.emulation.pixel_7', 'com.android.role.notes.enabled', 'com.google.android.apps.nexuslauncher', 'com.google.mainline.adservices', 'com.google.android.apps.wallpaper', 'com.android.internal.emulation.pixel_6_pro', 'com.google.android.federatedcompute', 'com.google.android.webview', 'com.google.android.sdksandbox', 'com.android.internal.emulation.pixel_3a', 'com.android.wallpaperbackup', 'com.android.systemui.emulation.pixel_6a', 'com.google.android.cellbroadcastservice', 'com.android.internal.systemui.navbar.twobutton', 'com.android.internal.systemui.navbar.threebutton', 'com.android.egg', 'com.android.systemui.emulation.pixel_fold', 'com.android.localtransport', 'android', 'com.android.camera2', 'com.android.systemui.emulation.pixel_3a_xl', 'com.android.providers.settings.auto_generated_rro_product__', 'com.google.android.soundpicker', 'com.google.android.packageinstaller', 'com.android.se', 'com.android.pacprocessor', 'com.google.android.connectivity.resources.goldfish.overlay', 'com.google.android.safetycenter.resources', 'com.google.android.apps.youtube.music', 'com.android.stk', 'com.android.internal.display.cutout.emulation.hole', 'com.android.settings', 'com.android.bips', 'com.google.android.partnersetup', 'com.android.internal.systemui.navbar.gestural_narrow_back', 'com.android.internal.display.cutout.emulation.tall', 'com.google.android.networkstack.tethering', 'com.android.systemui.emulation.pixel_7_pro', 'com.google.android.projection.gearhead', 'com.android.cameraextensions', 'com.google.android.odad', 'com.android.carrierconfig', 'com.android.internal.systemui.navbar.gestural_wide_back', 'com.google.android.ext.shared', 'com.google.android.feedback', 'com.android.chrome', 'com.google.android.apps.maps', 'com.google.android.as', 'android.auto_generated_rro_product__', 'com.android.musicfx', 'com.android.internal.systemui.navbar.transparent', 'com.android.server.telecom.auto_generated_rro_product__', 'com.google.android.inputmethod.latin', 'com.android.providers.settings.auto_generated_rro_vendor__', 'com.google.android.systemui.gxoverlay', 'com.google.android.uwb.resources', 'com.android.providers.downloads.ui', 'com.google.android.wifi.resources', 'com.android.ons', 'com.google.android.healthconnect.controller', 'com.android.intentresolver', 'com.google.android.apps.docs', 'com.google.android.nearby.halfsheet', 'com.android.phone.auto_generated_rro_vendor__', 'com.android.certinstaller', 'com.google.android.apps.restore', 'com.android.internal.emulation.pixel_7_pro', 'com.android.simappdialog', 'com.android.providers.telephony', 'com.android.wallpaper.livepicker', 'com.android.internal.display.cutout.emulation.emu01', 'com.android.internal.display.cutout.emulation.waterfall', 'com.android.settings.auto_generated_rro_product__', 'com.google.android.rkpdapp', 'com.android.providers.settings', 'com.android.systemui.emulation.pixel_3_xl', 'com.android.phone', 'com.android.internal.systemui.navbar.gestural_extra_wide_back', 'com.android.internal.emulation.pixel_4_xl', 'com.android.traceur', 'com.google.android.as.oss', 'com.google.android.apps.messaging', 'com.android.systemui.emulation.pixel_6_pro', 'com.android.internal.emulation.pixel_3a_xl', 'com.android.location.fused', 'com.android.vpndialogs', 'com.android.cellbroadcastreceiver', 'com.android.systemui.plugin.globalactions.wallet', 'com.google.android.tts', 'com.android.systemui.emulation.pixel_4_xl', 'com.google.android.googlequicksearchbox', 'com.google.android.modulemetadata', 'com.android.phone.auto_generated_rro_product__', 'com.android.systemui.accessibility.accessibilitymenu.auto_generated_rro_product__', 'com.android.htmlviewer', 'com.android.vending', 'com.google.android.ext.services', 'com.google.android.overlay.largescreensettingsprovider', 'com.google.android.configupdater', 'com.google.android.gms.supervision', 'com.android.providers.userdictionary', 'com.android.cts.ctsshim', 'com.google.android.apps.photos', 'com.android.bluetooth', 'com.google.android.markup', 'com.android.emulator.radio.config', 'com.android.internal.display.cutout.emulation.corner', 'com.google.android.gms', 'com.android.storagemanager', 'com.android.printspooler', 'com.android.systemui.auto_generated_rro_product__', 'com.android.providers.partnerbookmarks', 'com.android.soundpicker', 'com.google.mainline.telemetry', 'com.android.dynsystem', 'com.google.android.bluetooth', 'com.android.providers.telephony.auto_generated_rro_product__', 'com.google.android.connectivity.resources', 'com.android.bips.auto_generated_rro_product__', 'com.google.android.youtube', 'com.android.simappdialog.auto_generated_rro_product__', 'com.android.externalstorage', 'com.android.server.telecom']
# selected_idx = [13, 15, 51, 62, 67, 86, 111, 120, 121, 123, 137, 138, 153, 173, 187, 194, 211]
# app_list = [app_list[i] for i in selected_idx]

# rest is for API31
app_list = ['com.google.android.networkstack.tethering', 'com.android.cts.priv.ctsshim', 'com.google.android.youtube', 'com.android.internal.display.cutout.emulation.corner', 'com.google.android.ext.services', 'com.android.internal.display.cutout.emulation.double', 'com.android.providers.telephony', 'com.android.dynsystem', 'com.google.android.googlequicksearchbox', 'com.google.android.cellbroadcastservice', 'com.android.providers.calendar', 'com.android.providers.media', 'com.google.android.onetimeinitializer', 'com.google.android.ext.shared', 'com.android.internal.systemui.navbar.gestural_wide_back', 'com.android.managedprovisioning.auto_generated_rro_product__', 'com.android.carrierconfig.auto_generated_rro_vendor__', 'com.android.systemui.emulation.pixel_2_xl', 'com.android.systemui.emulation.pixel_3_xl', 'com.android.systemui.emulation.pixel_4_xl', 'com.android.simappdialog.auto_generated_rro_product__', 'com.android.externalstorage', 'com.android.htmlviewer', 'com.android.companiondevicemanager', 'com.android.mms.service', 'com.android.providers.downloads', 'com.android.systemui.auto_generated_rro_product__', 'com.google.android.apps.messaging', 'com.google.android.soundpicker', 'com.android.internal.systemui.onehanded.gestural', 'com.breel.wallpapers18', 'com.google.android.configupdater', 'com.google.android.providers.media.module', 'com.android.internal.emulation.pixel_4a', 'com.google.android.overlay.googlewebview', 'com.android.systemui.plugin.globalactions.wallet', 'com.android.providers.downloads.ui', 'com.google.android.hotspot2.osulogin', 'com.android.vending', 'com.android.pacprocessor', 'com.android.simappdialog', 'com.android.internal.display.cutout.emulation.hole', 'com.android.internal.display.cutout.emulation.tall', 'com.android.certinstaller', 'com.android.carrierconfig', 'com.android.internal.systemui.navbar.threebutton', 'android', 'com.android.contacts', 'com.android.camera2', 'com.android.egg', 'com.android.mtp', 'com.android.nfc', 'com.android.ons', 'com.android.stk', 'com.android.backupconfirm', 'com.android.systemui.auto_generated_rro_vendor__', 'com.google.android.deskclock', 'com.android.internal.systemui.navbar.twobutton', 'com.android.statementservice', 'com.google.android.gm', 'com.android.internal.systemui.navbar.gestural_extra_wide_back', 'com.google.android.permissioncontroller', 'com.android.systemui.emulation.pixel_3', 'com.android.systemui.emulation.pixel_4', 'com.android.systemui.emulation.pixel_5', 'com.google.android.setupwizard', 'com.android.emulator.radio.config', 'com.android.providers.settings', 'com.android.sharedstoragebackup', 'com.android.nfc.auto_generated_rro_product__', 'com.android.printspooler', 'com.android.emergency.auto_generated_rro_product__', 'com.android.dreams.basic', 'com.google.android.networkstack.tethering.emulator', 'com.android.providers.settings.auto_generated_rro_product__', 'com.android.se', 'com.android.inputdevices', 'com.android.traceur.auto_generated_rro_product__', 'com.google.android.apps.wellbeing', 'com.android.bips', 'com.android.internal.emulation.pixel_4', 'com.android.internal.emulation.pixel_5', 'com.google.android.captiveportallogin', 'com.android.musicfx', 'com.google.android.apps.docs', 'com.google.android.apps.maps', 'com.google.android.modulemetadata', 'com.android.internal.display.cutout.emulation.emu01', 'com.google.android.markup', 'com.android.providers.settings.auto_generated_rro_vendor__', 'com.android.cellbroadcastreceiver', 'com.google.android.webview', 'com.google.android.networkstack', 'com.google.android.apps.nexuslauncher.auto_generated_rro_vendor__', 'com.android.server.telecom', 'com.google.android.syncadapters.contacts', 'com.android.keychain', 'com.android.server.telecom.auto_generated_rro_product__', 'com.google.android.overlay.googleconfig', 'com.android.chrome', 'com.android.dialer', 'com.android.bips.auto_generated_rro_product__', 'com.google.android.packageinstaller', 'com.google.android.gms', 'com.google.android.gsf', 'com.google.android.tag', 'com.google.android.tts', 'com.google.android.overlay.permissioncontroller', 'com.google.android.overlay.emulatorconfig', 'com.android.calllogbackup', 'com.google.android.partnersetup', 'com.android.cameraextensions', 'com.google.android.apps.wallpaper.nexus', 'com.android.localtransport', 'com.google.android.apps.nexuslauncher', 'com.android.carrierdefaultapp', 'com.android.theme.font.notoserifsource', 'com.android.proxyhandler', 'com.android.internal.display.cutout.emulation.waterfall', 'org.chromium.webview_shell', 'com.google.android.connectivity.resources', 'com.android.providers.contacts.auto_generated_rro_product__', 'com.google.android.feedback', 'com.google.android.printservice.recommendation', 'com.google.android.apps.photos', 'com.google.android.calendar', 'com.android.managedprovisioning', 'com.android.soundpicker', 'com.google.android.documentsui', 'com.android.systemui.emulation.pixel_3a_xl', 'com.google.mainline.telemetry', 'com.android.emulator.multidisplay', 'com.android.providers.partnerbookmarks', 'com.android.wallpaper.livepicker', 'com.android.providers.telephony.auto_generated_rro_product__', 'com.android.phone.auto_generated_rro_vendor__', 'com.android.imsserviceentitlement', 'com.google.android.sdksetup', 'com.android.internal.emulation.pixel_2_xl', 'com.android.internal.emulation.pixel_3_xl', 'com.android.internal.emulation.pixel_4_xl', 'com.google.android.networkstack.permissionconfig', 'com.android.storagemanager', 'com.android.bookmarkprovider', 'com.google.android.overlay.pixelconfigcommon', 'com.android.settings', 'com.android.systemui.emulation.pixel_3a', 'com.android.systemui.emulation.pixel_4a', 'com.google.android.settings.intelligence', 'com.google.android.projection.gearhead', 'com.android.cts.ctsshim', 'com.google.android.wifi.resources', 'com.android.vpndialogs', 'com.google.android.apps.wallpaper', 'com.android.phone', 'com.android.shell', 'com.android.wallpaperbackup', 'com.android.providers.blockednumber', 'com.android.settings.auto_generated_rro_product__', 'com.android.providers.userdictionary', 'com.android.emergency', 'com.android.internal.systemui.navbar.gestural', 'com.android.location.fused', 'com.android.systemui', 'com.google.android.apps.youtube.music', 'com.android.bluetoothmidiservice', 'com.google.pixel.exo', 'com.android.traceur', 'com.android.storagemanager.auto_generated_rro_product__', 'com.google.android.cellbroadcastreceiver', 'com.android.phone.auto_generated_rro_product__', 'android.auto_generated_rro_product__', 'com.android.bluetooth', 'com.android.providers.contacts', 'com.android.internal.systemui.navbar.gestural_narrow_back', 'com.google.android.inputmethod.latin', 'android.auto_generated_rro_vendor__', 'com.google.android.apps.restore', '']
selected_idx = [2, 8, 27, 38, 47, 48, 53, 56, 59, 84, 85, 99, 100, 119, 124, 125, 128, 145, 164]
print(app_list)

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
             'I want to open my wifi', 'I need to open my hotspot',
             'I want to set Mulong as a quick-dial number, there should be a icon on the screen that I can directly call him by pressing it',
             'I want to take note "I like apple", and I want the phone use sound to read it for me',
             'I want to translate the "I like apple" into French', 'I need to go to the nearest market',
             'I want to see a youtube introducing canberra raiders', 'please tell me what time it is now in voice',
             'Can you help me clean my phone\'s memory?',
             'I want to cook a pasta for my son, I totally have no idea']

for task_idx, task in enumerate(task_list):
    if task_idx in [10, 13, 14, 18, 1, 3]:
        continue
    if task_idx < 5:
        continue
    # if task_idx < 15:
    #     continue
    task_id = f"task{task_idx+1}"
    # go homepage
    # device.go_homepage()

    # task declaration
    # task_declaration(task, max_try=10)

    user, task_obj = uta.instantiate_user_task(user_id, task_id)
    device.reboot_app(task_obj.involved_app_package)
    # task automation
    task_automation(max_try=20)

device.disconnect()
