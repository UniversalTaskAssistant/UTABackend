import cv2
from os.path import join as pjoin
from difflib import SequenceMatcher
from ._Data import _Data


class UIData(_Data):
    def __init__(self, screenshot_file, xml_file=None,
                 ui_resize=(1080, 2280), output_dir='data'):
        super().__init__()
        self.screenshot_file = screenshot_file
        self.xml_file = xml_file
        self.ui_no = screenshot_file.replace('/', '\\').split('\\')[-1].split('.')[0]

        # UI info
        self.ui_screenshot = cv2.resize(cv2.imread(screenshot_file), ui_resize)   # ui screenshot
        self.annotated_screenshot = None  # the screenshot with the drawn operation for debug
        self.ui_vh_json = None      # ui vh json, after processing

        # UI elements
        self.elements = []          # list of element in dictionary {'id':, 'class':...}
        self.elements_leaves = []   # leaf nodes that does not have children
        self.element_tree = None    # structural element tree, dict type
        self.blocks = []            # list of blocks from element tree
        self.ocr_text = []          # UI ocr detection result, list of __texts {}

        # output file paths
        self.output_dir = pjoin(output_dir, 'ui')
        self.output_file_path_elements = pjoin(self.output_dir, self.ui_no + '_elements.json')
        self.output_file_path_element_tree = pjoin(self.output_dir, self.ui_no + '_tree.json')

    def get_ui_element_node_by_id(self, ele_id):
        """
        Return UI element by its id
        Args:
            ele_id (str or int): The element ID
        Returns:
            Element node (dict): If found, otherwise None
        """
        def search_node_by_id(node, ele_id):
            '''
            Recursively search for node by element id, if not matched for current node, look into its children
            '''
            if node['id'] == ele_id:
                return node
            if node['id'] > ele_id:
                return None
            if 'children' in node:
                last_child = None
                for child in node['children']:
                    if child['id'] == ele_id:
                        return child
                    if child['id'] > ele_id:
                        break
                    last_child = child
                return search_node_by_id(last_child, ele_id)

        ele_id = int(ele_id)
        if ele_id >= len(self.elements):
            print('No element with id', ele_id, 'is found')
            return None
        return search_node_by_id(self.element_tree, ele_id)

    def check_ui_tree_similarity(self, ui_data2):
        """
        Compute the similarity between two uis by checking their element trees
        Args:
            ui_data2 (UIData): The comparing ui
        Returns:
            similarity (float): The similarity between two trees
        """
        return SequenceMatcher(None, str(self.element_tree), str(ui_data2.element_tree)).ratio()

    '''
    *********************
    *** Visualization ***
    *********************
    '''
    def show_each_element(self, only_leaves=False):
        """
        Show elements one by one
        Args:
            only_leaves (bool): True to just show element_leaves
        """
        board = self.ui_screenshot.copy()
        if only_leaves:
            elements = self.elements_leaves
            print(len(elements))
        else:
            elements = self.elements
        for ele in elements:
            print(ele['class'])
            print(ele, '\n')
            bounds = ele['bounds']
            clip = self.ui_screenshot[bounds[1]: bounds[3], bounds[0]: bounds[2]]
            color = (0, 255, 0) if not ele['clickable'] else (0, 0, 255)
            cv2.rectangle(board, (bounds[0], bounds[1]), (bounds[2], bounds[3]), color, 3)
            cv2.imshow('clip', cv2.resize(clip, (clip.shape[1] // 3, clip.shape[0] // 3)))
            cv2.imshow('ele', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            if cv2.waitKey() == ord('q'):
                break
        cv2.destroyAllWindows()

    def show_all_elements(self, only_leaves=False):
        """
        Show all elements at once
        Args:
            only_leaves (bool): True to just show element_leaves
        """
        board = self.ui_screenshot.copy()
        if only_leaves:
            elements = self.elements_leaves
        else:
            elements = self.elements
        for ele in elements:
            bounds = ele['bounds']
            color = (0, 255, 0) if not ele['clickable'] else (0, 0, 255)
            cv2.rectangle(board, (bounds[0], bounds[1]), (bounds[2], bounds[3]), color, 3)
        cv2.imshow('elements', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
        cv2.waitKey()
        cv2.destroyWindow('elements')

    def show_element_by_id(self, ele_id, show_children=True):
        """
        Show specific element by id
        Args:
            ele_id (int): id of element
            show_children (bool): True to show the children of the element
        """
        element = self.elements[ele_id]
        board = self.ui_screenshot.copy()
        color = (0,255,0) if not element['clickable'] else (0,0,255)
        bounds = element['bounds']
        cv2.rectangle(board, (bounds[0], bounds[1]), (bounds[2], bounds[3]), color, 3)
        if show_children and 'children-id' in element:
            for c_id in element['children-id']:
                bounds = self.elements[c_id]['bounds']
                cv2.rectangle(board, (bounds[0], bounds[1]), (bounds[2], bounds[3]), (255,0,255), 3)
        cv2.imshow('element', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
        cv2.waitKey()
        cv2.destroyWindow('element')

    def show_screen(self):
        """
        Show screenshot of the UI
        """
        cv2.imshow('screen', self.ui_screenshot)
        cv2.waitKey()
        cv2.destroyWindow('screen')

    def annotate_ui_operation(self, recommended_action):
        """
        Store annotated UI for debugging
        """
        assert recommended_action != "None"

        ele = self.elements[recommended_action.element_id]
        bounds = ele['bounds']

        if recommended_action.action.lower() == 'click':
            centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
            board = self.ui_screenshot.copy()
            cv2.circle(board, (centroid[0], centroid[1]), 20, (255, 0, 255), 8)
            self.annotated_screenshot = board
        elif recommended_action.action.lower() == 'long press':
            centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
            board = self.ui_screenshot.copy()
            cv2.circle(board, (centroid[0], centroid[1]), 20, (255, 0, 255), 8)
            self.annotated_screenshot = board
        elif recommended_action.action.lower() == 'scroll up':
            scroll_start = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
            scroll_end = ((bounds[2] + bounds[0]) // 2, bounds[1])
            board = self.ui_screenshot.copy()
            cv2.circle(board, scroll_start, 20, (255, 0, 255), 8)
            cv2.circle(board, scroll_end, 20, (255, 0, 255), 8)
            self.annotated_screenshot = board
        elif recommended_action.action.lower() == 'scroll down':
            scroll_end = ((bounds[2] + bounds[0]) // 2, bounds[3])
            scroll_start = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
            board = self.ui_screenshot.copy()
            cv2.circle(board, scroll_start, 20, (255, 0, 255), 8)
            cv2.circle(board, scroll_end, 20, (255, 0, 255), 8)
            self.annotated_screenshot = board
        elif recommended_action.action.lower() == 'swipe right':
            bias = 20
            swipe_start = (bounds[0] + bias, (bounds[3] + bounds[1]) // 2)
            swipe_end = (bounds[2], (bounds[3] + bounds[1]) // 2)
            board = self.ui_screenshot.copy()
            cv2.arrowedLine(board, swipe_start, swipe_end, (255, 0, 255), 8)
            self.annotated_screenshot = board
        elif recommended_action.action.lower() == 'swipe left':
            bias = 20
            swipe_start = (bounds[2] - bias, (bounds[3] + bounds[1]) // 2)
            swipe_end = (bounds[0], (bounds[3] + bounds[1]) // 2)
            board = self.ui_screenshot.copy()
            cv2.arrowedLine(board, swipe_start, swipe_end, (255, 0, 255), 8)
            self.annotated_screenshot = board
        elif recommended_action.action.lower() == 'input':
            text = recommended_action.input_text
            text_x = bounds[0] + 5  # Slightly right from the left bound
            text_y = (bounds[1] + bounds[3]) // 2  # Vertically centered
            board = self.ui_screenshot.copy()
            cv2.putText(board, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            self.annotated_screenshot = board
        else:
            self.annotated_screenshot = self.ui_screenshot.copy()
