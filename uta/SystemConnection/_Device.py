from ppadb.client import Client as AdbClient
import time
import cv2
from os.path import join as pjoin
import os
from uta.config import *


class _Device:
    def __init__(self, host='127.0.0.1', port=5037):
        self.__host = host
        self.__port = port
        self.__adb_device = None

    def connect(self, printlog=False):
        """
        Connects to the first device found on the ADB server.
        Args:
            printlog (bool): If True, prints the device information on connection.
        """
        if self.__adb_device is None:
            self.__adb_device = AdbClient(host=self.__host, port=self.__port).devices()[0]
            if printlog:
                print('=== Load Device - ' + self.get_device_name() + '-' + str(self.get_device_resolution()) + ' ===')
        else:
            # Raise an error if a device connection already exists
            raise Exception("Device has already been connected.")

    def is_connected(self):
        """
        Check whether the ADB device is connected.
        """
        if self.__adb_device is None:
            return False
        else:
            return True

    def disconnect(self):
        """
        Disconnects from the ADB device if a connection exists.
        """
        if self.__adb_device is not None:
            self.__adb_device = None

    '''
    ***********************
    *** Collect UI Data ***
    ***********************
    '''
    def cap_and_save_ui_screenshot_and_xml(self, ui_id, output_dir):
        """
        Capture and save ui screenshot and xml to target directory
        Args:
            ui_id (int or string): The id of the current ui, used to name the saved files
            output_dir (path): Directory to save img and xml
        Returns:
            screen_path, xml_path
        """
        os.makedirs(output_dir, exist_ok=True)
        screen_path = pjoin(output_dir, str(ui_id) + '.png')
        xml_path = pjoin(output_dir, str(ui_id) + '.xml')
        screen = self.cap_screenshot()
        with open(screen_path, 'wb') as fp:
            fp.write(screen)
        xml = self.cap_current_ui_hierarchy_xml()
        with open(xml_path, 'w') as fp:
            fp.write(xml)
        return screen_path, xml_path

    def cap_screenshot(self, recur_time=0):
        """
        Captures a screenshot of the current device screen.
        Args:
            recur_time (int): A counter for recursion, to retry capturing the screenshot, must be in [0, 3).
        Returns:
            Binary data of the captured screenshot.
        """
        assert 0 <= recur_time < 3
        screen = self.__adb_device.screencap()
        if recur_time and screen is None:
            screen = self.cap_screenshot(recur_time-1)
        return screen

    def cap_current_ui_hierarchy_xml(self):
        """
        Captures the current UI hierarchy of the device screen.
        Returns:
            XML content representing the UI hierarchy.
        """
        # Send the command to dump the UI hierarchy to an XML file on the device
        self.__adb_device.shell('uiautomator dump')

        # Read the content of the dumped XML file directly from the device
        xml_content = self.__adb_device.shell('cat /sdcard/window_dump.xml')
        return xml_content

    '''
    ***********
    *** App ***
    ***********
    '''
    def launch_app(self, package_name, waiting_time=2):
        """
        Launches an app on the device by its package name.
        Args:
            package_name (str): The package name of the app to launch.
            waiting_time (int): Time to wait after launching the app, in seconds.
        """
        print('--- Launch app:', package_name, '---')
        self.__adb_device.shell(f'monkey -p {package_name} -c android.intent.category.LAUNCHER 1')
        time.sleep(waiting_time)

    def close_app(self, package_name, waiting_time=2):
        """
        Force stops an app on the device by its package name.
        Args:
            package_name (str): The package name of the app to close.
            waiting_time (int): Time to wait after closing the app, in seconds.
        """
        print('--- Close app:', package_name, '---')
        self.__adb_device.shell(f'am force-stop {package_name}')
        time.sleep(waiting_time)

    def get_app_list_on_the_device(self):
        """
        Retrieves a list of all installed applications on the device.
        Returns:
            A list of package names of the installed applications.
        """
        packages = self.__adb_device.shell('pm list packages')
        package_list = packages.split('\n')
        return [p.replace('package:', '') for p in package_list]

    def get_current_package_and_activity_name(self):
        """
        Retrieves the current foreground package and activity name.
        Returns:
            A dictionary with 'package_name' and 'activity_name'.
        """
        dumpsys_output = self.__adb_device.shell('dumpsys window displays | grep mCurrentFocus')
        package_and_activity = dumpsys_output.split('u0 ')[1].split('}')[0]
        package_name, activity_name = package_and_activity.split('/')
        return {'package_name': package_name, 'activity_name': activity_name}

    '''
    ***********************
    *** Get Device Info ***
    ***********************
    '''
    def check_keyboard_active(self):
        """
        Checks if the keyboard is active (visible) on the device.
        Returns:
            True if the keyboard is visible, False otherwise.
        """
        dumpsys_output = self.__adb_device.shell('dumpsys input_method | grep mInputShown')
        if 'mInputShown=true' in dumpsys_output:
            return True
        return False

    def get_device(self):
        """
        Retrieves the current ADB device object.
        Returns:
            The ADB device object.
        """
        return self.__adb_device

    def get_device_name(self):
        """
        Retrieves the serial number of the connected device.
        Returns:
            The serial number of the device.
        """
        return self.__adb_device.get_serial_no()

    def get_device_resolution(self):
        """
        Retrieves the screen resolution of the connected device.
        Returns:
            The screen resolution as a tuple (width, height).
        """
        return self.__adb_device.wm_size()

    '''
    ***************
    *** Actions ***
    ***************
    '''
    def click_screen(self, ui, element, show=False):
        """
        Simulates a tap on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element: The key for the element in the UI to tap.
            show (bool): If True, displays the tap visually.
        """
        ele = ui.elements[element]
        bounds = ele['bounds']
        centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
        if show:
            board = ui.img.copy()
            cv2.circle(board, (centroid[0], centroid[1]), 20, (255, 0, 255), 8)
            cv2.imshow('click', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            cv2.waitKey()
            cv2.destroyWindow('click')
        self.__adb_device.input_tap(centroid[0], centroid[1])

    def long_press_screen(self, ui, element, show=False):
        """
        Simulates a long press on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element: The key for the element in the UI to long press.
            show (bool): If True, displays the long press visually.
        """
        ele = ui.elements[element]
        bounds = ele['bounds']
        centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
        if show:
            board = ui.img.copy()
            cv2.circle(board, (centroid[0], centroid[1]), 20, (255, 0, 255), 8)
            cv2.imshow('long_press', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            cv2.waitKey()
            cv2.destroyWindow('long_press')
        self.__adb_device.input_swipe(centroid[0], centroid[1], centroid[0], centroid[1], 3000)

    def up_scroll_screen(self, ui, element, show=False):
        """
        Simulates an upward scroll on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element: The key for the element in the UI to scroll up.
            show (bool): If True, displays the scroll action visually.
        """
        ele = ui.elements[element]
        bounds = ele['bounds']
        scroll_start = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
        scroll_end = ((bounds[2] + bounds[0]) // 2, bounds[1])
        if show:
            board = ui.img.copy()
            cv2.arrowedLine(board, scroll_start, scroll_end, (255, 0, 255), 8)
            cv2.imshow('up_scroll', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            cv2.waitKey()
            cv2.destroyWindow('up_scroll')
        self.__adb_device.input_swipe(scroll_start[0], scroll_start[1], scroll_end[0], scroll_end[1], 500)

    def down_scroll_screen(self, ui, element, show=False):
        """
        Simulates a downward scroll on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element: The key for the element in the UI to scroll down.
            show (bool): If True, displays the scroll action visually.
        """
        ele = ui.elements[element]
        bounds = ele['bounds']
        scroll_end = ((bounds[2] + bounds[0]) // 2, bounds[3])
        scroll_start = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
        if show:
            board = ui.img.copy()
            cv2.arrowedLine(board, scroll_start, scroll_end, (255, 0, 255), 8)
            cv2.imshow('down_scroll', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            cv2.waitKey()
            cv2.destroyWindow('down_scroll')
        self.__adb_device.input_swipe(scroll_start[0], scroll_start[1], scroll_end[0], scroll_end[1], 500)

    def right_swipe_screen(self, ui, element, show=False):
        """
        Simulates a right swipe on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element: The key for the element in the UI to swipe right.
            show (bool): If True, displays the swipe action visually.
        """
        ele = ui.elements[element]
        bounds = ele['bounds']
        bias = 20
        swipe_start = (bounds[0] + bias, (bounds[3] + bounds[1]) // 2)
        swipe_end = (bounds[2], (bounds[3] + bounds[1]) // 2)
        if show:
            board = ui.img.copy()
            cv2.arrowedLine(board, swipe_start, swipe_end, (255, 0, 255), 8)
            cv2.imshow('right_swipe', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            cv2.waitKey()
            cv2.destroyWindow('right_swipe')
        self.__adb_device.input_swipe(swipe_start[0], swipe_start[1], swipe_end[0], swipe_end[1], 500)

    def left_swipe_screen(self, ui, element, show=False):
        """
        Simulates a left swipe on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element: The key for the element in the UI to swipe left.
            show (bool): If True, displays the swipe action visually.
        """
        ele = ui.elements[element]
        bounds = ele['bounds']
        bias = 20
        swipe_start = (bounds[2] - bias, (bounds[3] + bounds[1]) // 2)
        swipe_end = (bounds[0], (bounds[3] + bounds[1]) // 2)
        if show:
            board = ui.img.copy()
            cv2.arrowedLine(board, swipe_start, swipe_end, (255, 0, 255), 8)
            cv2.imshow('left_swipe', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            cv2.waitKey()
            cv2.destroyWindow('left_swipe')
        self.__adb_device.input_swipe(swipe_start[0], swipe_start[1], swipe_end[0], swipe_end[1], 500)

    def input_text(self, text):
        """
        Inputs text into the currently focused field on the device.
        Args:
            text (str): The text to input.
        """
        self.__adb_device.input_text(text)

    def go_back(self, waiting_time=2):
        """
        Simulates the 'Back' button press on the device.
        Args:
            waiting_time (int): Time to wait after the action, in seconds.
        """
        self.__adb_device.shell('input keyevent KEYCODE_BACK')
        # wait a few second to be refreshed
        time.sleep(waiting_time)


if __name__ == '__main__':
    device = _Device()
    device.connect()
    device.get_app_list_on_the_device()
    device.cap_and_save_ui_screenshot_and_xml(1, WORK_PATH + 'data/device')
