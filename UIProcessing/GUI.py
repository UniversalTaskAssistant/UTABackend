import cv2
import numpy as np


class GUI:
    def __init__(self, gui_img_file, gui_json_file, gui_resize):
        """
        Initializes the GUI object.
        Args:
            gui_img_file: Binary data of the GUI image.
            gui_json_file: JSON file containing GUI element data.
            gui_resize: Tuple for resizing the GUI image (width, height).
        """
        self.json = gui_json_file  # Store the path or data of the GUI JSON file

        # Processing the image file
        image_array = np.frombuffer(gui_img_file, dtype=np.uint8)  # Convert the binary data to a NumPy array
        image_cv2 = cv2.imdecode(image_array, cv2.IMREAD_COLOR)  # Decode the image array into an OpenCV image
        self.img = cv2.resize(image_cv2, gui_resize)  # Resize the image

        # Initialize GUI elements and structure
        self.element_id = 0
        self.elements = []  # list of element in dictionary {'id':, 'class':...}
        self.elements_leaves = []  # leaf nodes that does not have children
        self.element_tree = {}  # structural element tree, dict type
        self.blocks = []  # list of blocks from element tree
        self.removed_node_no = 0  # for the record of the number of removed nodes

        self.ocr_text = []  # GUI ocr detection result, list of texts {}

    def load_elements(self, elements, element_tree):
        """
        Loads GUI elements and their structural tree.
        Args:
            elements: List of GUI elements.
            element_tree: Hierarchical tree structure of GUI elements.
        """
        self.elements = elements  # Load the elements
        self.element_id = self.elements[-1]['id'] + 1 if len(self.elements) > 0 else 0  # Set the next element ID
        self.element_tree = element_tree  # Load the element tree structure
