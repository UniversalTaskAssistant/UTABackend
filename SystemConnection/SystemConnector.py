import os

from SystemConnection._Device import _Device
from SystemConnection._Local import _Local
from DataStructures.config import *


class SystemConnector:
    def __init__(self):
        """
        Initializes a SystemConnector instance.
        """
        self.__adb_device = _Device()
        self.__local = _Local()

    '''
    ****************
    *** Local IO ***
    ****************
    '''
    def load_xml(self, file_path, encoding='utf-8'):
        """
        Loads and parses an XML file.
        Args:
            file_path (str): Path to the XML file.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        Returns:
            Parsed XML content.
        """
        return self.__local.load_xml(file_path, encoding)

    def load_img(self, file_path):
        """
        Loads an image file as a binary stream.
        Args:
            file_path (str): Path to the image file.
        Returns:
            Binary content of the image file.
        """
        return self.__local.load_img(file_path)

    def load_json(self, file_path, encoding='utf-8'):
        """
        Loads a JSON file.
        Args:
            file_path (str): Path to the JSON file.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        Returns:
            Parsed JSON data.
        """
        return self.__local.load_json(file_path, encoding)

    def save_xml(self, file, file_path, encoding='utf-8'):
        """
        Saves a dictionary as an XML file.
        Args:
            file (dict): Dictionary to save as XML.
            file_path (str): Path where the XML file will be saved.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.__local.save_xml(file, file_path, encoding)

    def save_img(self, img, file_path):
        """
        Saves binary image data to a file.
        Args:
            img (bytes): Binary image data to save.
            file_path (str): Path where the image file will be saved.
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.__local.save_img(img, file_path)

    def save_json(self, file, file_path, encoding='utf-8'):
        """
        Saves a dictionary as a JSON file.
        Args:
            file (dict): Dictionary to save as JSON.
            file_path (str): Path where the JSON file will be saved.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.__local.save_json(file, file_path, encoding)

    '''
    ******************
    *** Adb Device ***
    ******************
    Can only be used in emulator mode
    '''
    def connect_adb_device(self, printlog=False):
        """
        Connects to the first device found on the ADB server.
        Args:
            printlog (bool): If True, prints the device information on connection.
        """
        self.__adb_device.connect(printlog)

    def is_connected(self):
        """
        Check whether the ADB device is connected.
        """
        return self.__adb_device.is_connected()

    def disconnect_device(self):
        """
        Disconnects from the ADB device if a connection exists.
        """
        self.__adb_device.disconnect()

    def go_back(self, waiting_time=2):
        """
        Simulates the 'Back' button press on the device.
        Args:
            waiting_time (int): Time to wait after the action, in seconds.
        """
        self.__adb_device.go_back(waiting_time)

    def launch_app(self, package_name, waiting_time=2):
        """
        Launches an app on the device by its package name.
        Args:
            package_name (str): The package name of the app to launch.
            waiting_time (int): Time to wait after launching the app, in seconds.
        """
        self.__adb_device.launch_app(package_name, waiting_time)

    def close_app(self, package_name, waiting_time=2):
        """
        Force stops an app on the device by its package name.
        Args:
            package_name (str): The package name of the app to close.
            waiting_time (int): Time to wait after closing the app, in seconds.
        """
        self.__adb_device.close_app(package_name, waiting_time)

    def check_keyboard_active(self):
        """
        Checks if the keyboard is active (visible) on the device.
        Returns:
            True if the keyboard is visible, False otherwise.
        """
        return self.__adb_device.check_keyboard_active()

    def get_app_list_on_the_device(self):
        """
        Retrieves a list of all installed applications on the device.
        Returns:
            A list of package names of the installed applications.
        """
        return self.__adb_device.get_app_list_on_the_device()

    def cap_and_save_ui_screenshot_and_xml(self, ui_id, output_dir):
        """
        Capture and save ui screenshot and xml to target directory
        Args:
            ui_id (int or string): The id of the current ui, used to name the saved files
            output_dir (path): Directory to save img and xml
        Returns:
            screen_path, xml_path
        """
        return self.__adb_device.cap_and_save_ui_screenshot_and_xml(ui_id, output_dir)

    def cap_screenshot(self, recur_time=0):
        """
        Captures a screenshot of the current device screen.
        Args:
            recur_time (int): A counter for recursion, to retry capturing the screenshot.
        Returns:
            Binary data of the captured screenshot.
        """
        return self.__adb_device.cap_screenshot(recur_time)

    def cap_current_ui_hierarchy(self):
        """
        Captures the current UI hierarchy of the device screen.
        Returns:
            XML content representing the UI hierarchy.
        """
        return self.__adb_device.cap_current_ui_hierarchy_xml()

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
        return self.__adb_device.get_device_name()

    def get_device_resolution(self):
        """
        Retrieves the screen resolution of the connected device.
        Returns:
            The screen resolution as a tuple (width, height).
        """
        return self.__adb_device.get_device_resolution()

    def get_current_package_and_activity_name(self):
        """
        Retrieves the current foreground package and activity name.
        Returns:
            A dictionary with 'package_name' and 'activity_name'.
        """
        return self.__adb_device.get_current_package_and_activity_name()

    def click_screen(self, ui, element, show=False):
        """
        Simulates a tap on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element: The key for the element in the UI to tap.
            show (bool): If True, displays the tap visually.
        """
        self.__adb_device.click_screen(ui, element, show)

    def long_press_screen(self, ui, element, show=False):
        """
        Simulates a long press on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element: The key for the element in the UI to long press.
            show (bool): If True, displays the long press visually.
        """
        self.__adb_device.long_press_screen(ui, element, show)

    def up_scroll_screen(self, ui, element, show=False):
        """
        Simulates an upward scroll on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element: The key for the element in the UI to scroll up.
            show (bool): If True, displays the scroll action visually.
        """
        self.__adb_device.up_scroll_screen(ui, element, show)

    def down_scroll_screen(self, ui, element, show=False):
        """
        Simulates a downward scroll on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element: The key for the element in the UI to scroll down.
            show (bool): If True, displays the scroll action visually.
        """
        self.__adb_device.down_scroll_screen(ui, element, show)

    def right_swipe_screen(self, ui, element, show=False):
        """
        Simulates a right swipe on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element: The key for the element in the UI to swipe right.
            show (bool): If True, displays the swipe action visually.
        """
        self.__adb_device.right_swipe_screen(ui, element, show)

    def left_swipe_screen(self, ui, element, show=False):
        """
        Simulates a left swipe on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element: The key for the element in the UI to swipe left.
            show (bool): If True, displays the swipe action visually.
        """
        self.__adb_device.left_swipe_screen(ui, element, show)

    def input_text(self, text):
        """
        Inputs text into the currently focused field on the device.
        Args:
            text (str): The text to input.
        """
        self.__adb_device.input_text(text)


if __name__ == '__main__':
    sys_connector = SystemConnector()
    sys_connector.connect_adb_device()
    screen_path, xml_path = sys_connector.cap_and_save_ui_screenshot_and_xml(1, WORK_PATH + 'data/device')
