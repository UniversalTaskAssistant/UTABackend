import requests
import json
from base64 import b64encode
import time
import cv2
from os.path import join as pjoin

from uta.DataStructures.Text import Text
from config import *


class _GoogleOCR:
    def __init__(self):
        self.__url = 'https://vision.googleapis.com/v1/images:annotate'
        self.__api_key = open(WORK_PATH + 'uta/ModelManagement/VisionModel/googleapikey.txt', 'r').readline()

        self.org_img = None     # cv2.img, original image
        self.ocr_result = None  # original results from google ocr
        self.__texts = []         # list of _Text for intermediate processing results

    @staticmethod
    def __make_image_data(img_path):
        """
        Prepares the image data for the API request.
        Args:
            img_path (str): Image file path.
        Returns:
            Encoded JSON data to be sent in the API request.
        """
        with open(img_path, 'rb') as f:
            ctxt = b64encode(f.read()).decode()
            # Setting up the request parameters for the OCR
            img_req = {
                'image': {
                    'content': ctxt
                },
                'features': [{
                    'type': 'DOCUMENT_TEXT_DETECTION',
                    # 'type': 'TEXT_DETECTION',
                    'maxResults': 1
                }]
            }
        return json.dumps({"requests": img_req}).encode()

    def __text_cvt_orc_format(self, ocr_result):
        '''
        Convert ocr result format for easier processing
        Args:
            ocr_result: [{'description': '5:08', 'boundingPoly': {'vertices': [{'x': 58, 'y': 16}, {'x': 113, 'y': 15},
             {'x': 113, 'y': 35}, {'x': 58, 'y': 36}]}}]
        Returns:
            __texts: [{'id': 0, 'bounds': [77, 20, 151, 48], 'content': '5:08'}]
        '''
        if ocr_result is not None:
            for i, result in enumerate(ocr_result):
                error = False
                x_coordinates = []
                y_coordinates = []
                text_location = result['boundingPoly']['vertices']
                content = result['description']
                for loc in text_location:
                    if 'x' not in loc or 'y' not in loc:
                        error = True
                        break
                    x_coordinates.append(loc['x'])
                    y_coordinates.append(loc['y'])
                if error: continue
                location = {'left': min(x_coordinates), 'top': min(y_coordinates),
                            'right': max(x_coordinates), 'bottom': max(y_coordinates)}
                self.__texts.append(Text(i, content, location))

    def __merge_intersected_texts(self):
        '''
        Merge intersected __texts (sentences or words)
        '''
        changed = True
        while changed:
            changed = False
            temp_set = []
            for text_a in self.__texts:
                merged = False
                for text_b in temp_set:
                    if text_a.is_intersected(text_b, bias=2):
                        text_b.merge_text(text_a)
                        merged = True
                        changed = True
                        break
                if not merged:
                    temp_set.append(text_a)
            self.__texts = temp_set.copy()

    def __text_filter_noise(self):
        '''
        Filter out some noise text that is abnormal single character
        '''
        valid_texts = []
        for text in self.__texts:
            if len(text.content) <= 1 and text.content.lower() not in ['a', ',', '.', '!', '?', '$', '%', ':', '&',
                                                                       '+']:
                continue
            valid_texts.append(text)
        self.__texts = valid_texts

    def __text_sentences_recognition(self):
        '''
        Merge separate words detected by Google ocr into a sentence
        '''
        changed = True
        while changed:
            changed = False
            temp_set = []
            for text_a in self.__texts:
                merged = False
                for text_b in temp_set:
                    if text_a.is_on_same_line(text_b, 'h', bias_justify=0.2 * min(text_a.height, text_b.height),
                                              bias_gap=1.3 * max(text_a.word_width, text_b.word_width)):
                        text_b.merge_text(text_a)
                        merged = True
                        changed = True
                        break
                if not merged:
                    temp_set.append(text_a)
            self.__texts = temp_set.copy()
        for i, text in enumerate(self.__texts):
            text.id = i

    def __resize_label(self, shrink_rate):
        '''
        Resize the labels of text by certain ratio
        Args:
            shrink_rate: rate to resize
        '''
        for text in self.__texts:
            for key in text.location:
                text.location[key] = round(text.location[key] / shrink_rate)

    def __wrap_up_texts(self):
        '''
        Wrap up Text objects to list of dicts
        Args:
            self.__texts (list of _Text)
        Returns:
            texts_dict (list of dict): [{'id': 0, 'bounds': [77, 20, 151, 48], 'content': '5:08'}]
        '''
        texts_dict = []
        for i, text in enumerate(self.__texts):
            loc = text.location
            t = {'id': i,
                 'bounds': [loc['left'], loc['top'], loc['right'], loc['bottom']],
                 'content': text.content}
            texts_dict.append(t)
        return texts_dict

    def visualize_texts(self, shown_resize_height=800, show=False, write_path=None):
        '''
        Visualize the __texts
        Args:
            shown_resize_height: The height of the shown image for better view
            show (bool): True to show on popup window
            write_path (sting): Path to save the visualized image, None for not saving
        Returns:

        '''
        img = self.org_img.copy()
        for text in self.__texts:
            text.visualize_element(img, line=2)
        img_resize = img
        if shown_resize_height is not None:
            img_resize = cv2.resize(img, (int(shown_resize_height * (img.shape[1] / img.shape[0])),
                                          shown_resize_height))

        if show:
            cv2.imshow('__texts', img_resize)
            cv2.waitKey(0)
            cv2.destroyWindow('__texts')
        if write_path is not None:
            cv2.imwrite(write_path, img_resize)
        return img_resize

    def save_detection_json(self, file_path):
        '''
        Save the Text to local as json file
        Args:
            file_path: File to save
        '''
        f_out = open(file_path, 'w')
        output = {'img_shape': self.org_img.shape, '__texts': []}
        for text in self.__texts:
            c = {'id': text.id, 'content': text.content}
            loc = text.location
            c['column_min'], c['row_min'], c['column_max'], c['row_max'] = loc['left'], loc['top'], loc['right'], \
                                                                           loc['bottom']
            c['width'] = text.width
            c['height'] = text.height
            output['__texts'].append(c)
        json.dump(output, f_out, indent=4)

    def request_google_ocr(self, img_path):
        """
        Sends an OCR request to the Google Cloud Vision API.
        Args:
            img_path (str): Image file path.
        Returns:
            The detected text annotations or None if no text is found.
        """
        try:
            img_data = self.__make_image_data(img_path)  # Prepare the image data

            # Post request to the Google Cloud Vision API
            response = requests.post(self.__url,
                                     data=img_data,
                                     params={'key': self.__api_key},
                                     headers={'Content_Type': 'application/json'})

            # Handling the API response
            if 'responses' not in response.json():
                raise Exception(response.json())
            if response.json()['responses'] == [{}]:
                return None  # Return None if no text is detected
            else:
                self.ocr_result = response.json()['responses'][0]['textAnnotations'][1:]
                return self.ocr_result
        except Exception as e:
            raise e

    def detect_text_ocr(self, img_path, output_dir='data/output', show=False, shrink_size=False):
        '''
        Detect __texts on the image using google ocr
        Args:
            img_path: The file path of the image
            output_dir: Directory to store the output
            show (bool): True to visualize the result
            shrink_size (bool): True to shrink the image before processing for faster speed
        Returns:
            __texts (list of dicts): [{'id': 0, 'bounds': [77, 20, 151, 48], 'content': '5:08'}]
        '''
        start = time.time()
        name = img_path.replace('\\', '/').split('/')[-1][:-4]
        self.org_img = cv2.imread(img_path)
        if shrink_size:
            shrink_rate = 0.75
            img_re = cv2.resize(self.org_img, (int(self.org_img.shape[1] * shrink_rate), int(self.org_img.shape[0]
                                                                                             * shrink_rate)))
            img_path = img_path[:-4] + '_resize.jpg'
            cv2.imwrite(img_path, img_re)

        self.request_google_ocr(img_path)
        self.__text_cvt_orc_format(self.ocr_result)
        self.__merge_intersected_texts()
        self.__text_filter_noise()
        self.__text_sentences_recognition()
        if shrink_size:
            self.__resize_label(shrink_rate)
        if show:
            self.visualize_texts(show=True)
            print("[Text Detection Completed in %.3f s] Input: %s Output: %s" % (time.time() - start, img_path,
                                                                                 pjoin(output_dir, name + '.json')))
        return self.__wrap_up_texts()


if __name__ == '__main__':
    google = _GoogleOCR()
    google.detect_text_ocr(img_path=WORK_PATH + '/data/0.png', output_dir=WORK_PATH + '/data/ocr',
                           shrink_size=True, show=True)
