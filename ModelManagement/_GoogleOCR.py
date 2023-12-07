import requests
import json


class _GoogleOCR:
    def __init__(self):
        self.__url = 'https://vision.googleapis.com/v1/images:annotate'
        self.__api_key = open('ModelManagement/googleapikey.txt', 'r').readline()

    def __make_image_data(self, ctxt):
        """
        Prepares the image data for the API request.
        Args:
            ctxt (str): The base64 encoded string of the image.
        Returns:
            Encoded JSON data to be sent in the API request.
        """
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

    def detect_ocr(self, ctxt):
        """
        Sends an OCR request to the Google Cloud Vision API.
        Args:
            ctxt (str): The base64 encoded string of the image.
        Returns:
            The detected text annotations or None if no text is found.
        """
        try:
            img_data = self.__make_image_data(ctxt)  # Prepare the image data

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
                return response.json()['responses'][0]['textAnnotations'][1:]
        except Exception as e:
            raise e