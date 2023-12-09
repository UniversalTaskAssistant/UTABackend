from ppadb.client import Client as AdbClient
import time
import cv2


class _Device:
    def __init__(self, host='127.0.0.1', port=5037):
        self.__host = host
        self.__port = port
        self.__adb_device = None

    def connect(self, printlog=False):
        if self.__adb_device is None:
            self.__adb_device = AdbClient(host=self.__host, port=self.__port).devices()[0]
            if printlog:
                print('=== Load Device - ' + self.get_device_name() + '-' + str(self.get_device_resolution()) + ' ===')
        else:
            # Raise an error if a device connection already exists
            raise Exception("Device has already been connected.")

    def disconnect(self):
        """
            Disconnects from the ADB device if a connection exists.
            """
        if self.__adb_device is not None:
            self.__adb_device = None

    def go_back(self, waiting_time=2):
        self.__adb_device.shell('input keyevent KEYCODE_BACK')
        # wait a few second to be refreshed
        time.sleep(waiting_time)

    def launch_app(self, package_name, waiting_time=2):
        print('--- Launch app:', package_name, '---')
        self.__adb_device.shell(f'monkey -p {package_name} -c android.intent.category.LAUNCHER 1')
        time.sleep(waiting_time)

    def close_app(self, package_name, waiting_time=2):
        print('--- Close app:', package_name, '---')
        self.__adb_device.shell(f'am force-stop {package_name}')
        time.sleep(waiting_time)

    def check_keyboard_active(self):
        dumpsys_output = self.__adb_device.shell('dumpsys input_method | grep mInputShown')
        if 'mInputShown=true' in dumpsys_output:
            return True
        return False

    def get_app_list_on_the_device(self):
        packages = self.__adb_device.shell('pm list packages')
        package_list = packages.split('\n')
        return [p.replace('package:', '') for p in package_list]

    def cap_screenshot(self, recur_time=0):
        assert recur_time < 3
        screen = self.__adb_device.screencap()
        if recur_time and screen is None:
            self.cap_screenshot(recur_time+1)
        return screen

    def cap_current_ui_hierarchy(self):
        # Send the command to dump the UI hierarchy to an XML file on the device
        self.__adb_device.shell('uiautomator dump')

        # Read the content of the dumped XML file directly from the device
        xml_content = self.__adb_device.shell('cat /sdcard/window_dump.xml')
        return xml_content

    def get_device(self):
        return self.__adb_device

    def get_device_name(self):
        return self.__adb_device.get_serial_no()

    def get_device_resolution(self):
        return self.__adb_device.wm_size()

    def get_current_package_and_activity_name(self):
        dumpsys_output = self.__adb_device.shell('dumpsys window displays | grep mCurrentFocus')
        package_and_activity = dumpsys_output.split('u0 ')[1].split('}')[0]
        package_name, activity_name = package_and_activity.split('/')
        return {'package_name': package_name, 'activity_name': activity_name}

    def click_screen(self, gui, element, show=False):
        ele = gui.elements[element]
        bounds = ele['bounds']
        centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
        if show:
            board = gui.img.copy()
            cv2.circle(board, (centroid[0], centroid[1]), 20, (255, 0, 255), 8)
            cv2.imshow('click', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            cv2.waitKey()
            cv2.destroyWindow('click')
        self.__adb_device.input_tap(centroid[0], centroid[1])

    def long_press_screen(self, gui, element, show=False):
        ele = gui.elements[element]
        bounds = ele['bounds']
        centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
        if show:
            board = gui.img.copy()
            cv2.circle(board, (centroid[0], centroid[1]), 20, (255, 0, 255), 8)
            cv2.imshow('long_press', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            cv2.waitKey()
            cv2.destroyWindow('long_press')
        self.__adb_device.input_swipe(centroid[0], centroid[1], centroid[0], centroid[1], 3000)

    def scroll_screen(self, gui, element, show=False):
        ele = gui.elements[element]
        bounds = ele['bounds']
        bias = 5
        if show:
            board = gui.img.copy()
            cv2.circle(board, (bounds[2] - bias, bounds[3] + bias), 20, (255, 0, 255), 8)
            cv2.circle(board, (bounds[0] - bias, bounds[1] + bias), 20, (255, 0, 255), 8)
            cv2.imshow('scroll', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            cv2.waitKey()
            cv2.destroyWindow('scroll')
        self.__adb_device.input_swipe(bounds[2] - bias, bounds[3] + bias, bounds[0] - bias, bounds[1] + bias, 500)

    def right_swipe_screen(self, gui, element, show=False):
        ele = gui.elements[element]
        bounds = ele['bounds']
        centroid_start = (bounds[0], (bounds[3] + bounds[1]) // 2)
        centroid_end = (bounds[2], (bounds[3] + bounds[1]) // 2)
        if show:
            board = gui.img.copy()
            cv2.arrowedLine(board, centroid_start, centroid_end, (255, 0, 255), 8)
            cv2.imshow('right_swipe', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            cv2.waitKey()
            cv2.destroyWindow('right_swipe')
        self.__adb_device.input_swipe(centroid_start[0], centroid_start[1], centroid_end[0], centroid_end[1], 500)

    def left_swipe_screen(self, gui, element, show=False):
        ele = gui.elements[element]
        bounds = ele['bounds']
        centroid_start = (bounds[2], (bounds[3] + bounds[1]) // 2)
        centroid_end = (bounds[0], (bounds[3] + bounds[1]) // 2)
        if show:
            board = gui.img.copy()
            cv2.arrowedLine(board, centroid_start, centroid_end, (255, 0, 255), 8)
            cv2.imshow('left_swipe', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            cv2.waitKey()
            cv2.destroyWindow('left_swipe')
        self.__adb_device.input_swipe(centroid_start[0], centroid_start[1], centroid_end[0], centroid_end[1], 500)

    def input_text(self, text):
        self.__adb_device.input_text(text)