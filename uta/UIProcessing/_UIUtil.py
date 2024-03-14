from difflib import SequenceMatcher
import pyshine as ps
import cv2


class _UIUtil:
    def __init__(self):
        pass

    @staticmethod
    def get_ui_element_node_by_id(ui_data, ele_id):
        """
        Return UI element by its id
        Args:
            ui_data (UIData): Target UIData
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
        if ele_id >= len(ui_data.elements):
            print('No element with id', ele_id, 'is found')
            return None
        return search_node_by_id(ui_data.element_tree, ele_id)

    @staticmethod
    def check_ui_tree_similarity(ui_data1, ui_data2):
        """
        Compute the similarity between two uis by checking their element trees
        Args:
            ui_data1 (UIData): The comparing ui
            ui_data2 (UIData): The comparing ui
        Returns:
            similarity (float): The similarity between two trees
        """
        return SequenceMatcher(None, str(ui_data1.element_tree), str(ui_data2.element_tree)).ratio()

    @staticmethod
    def annotate_elements_with_id(ui_data, only_leaves=True, show=True):
        """
        Annotate elements on the ui screenshot using IDs
        Args:
            ui_data (UIData): Target UIData
            only_leaves (bool): True to just show element_leaves
            show (bool): True to show the result
        Returns:
            annotated_img (cv2 image): Annotated UI screenshot
        """
        board = ui_data.ui_screenshot.copy()
        if only_leaves:
            elements = ui_data.elements_leaves
        else:
            elements = ui_data.elements
        # draw bounding box
        # for ele in elements:
        #     left, top, right, bottom = ele['bounds']
        #     cv2.rectangle(board, (left, top), (right, bottom), (0, 250, 0), 3)
        # annotate elements
        for i, ele in enumerate(elements):
            left, top, right, bottom = ele['bounds']
            try:
                # mark on the top if possible
                board = ps.putBText(board, str(ele['id']), text_offset_x=(left + right) // 2, text_offset_y=top - 5,
                                    vspace=10, hspace=10, font_scale=1, thickness=2, background_RGB=(10,10,10),
                                    text_RGB=(200,200,200), alpha=0.55)
            except ValueError as e:
                # else mark on the bottom
                board = ps.putBText(board, str(ele['id']), text_offset_x=(left + right) // 2, text_offset_y=bottom,
                                    vspace=10, hspace=10, font_scale=1, thickness=2, background_RGB=(10,10,10),
                                    text_RGB=(200,200,200), alpha=0.55)
        if show:
            cv2.imshow('a', cv2.resize(board, (500, 1000)))
            cv2.waitKey()
            cv2.destroyAllWindows()
        return board