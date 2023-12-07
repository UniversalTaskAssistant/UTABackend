from ModelManagement import _GoogleOCR, _IconClassifier


class _VisionModel:
    def __init__(self):
        self.__google_ocr = _GoogleOCR()
        self.__icon_classifier = _IconClassifier()

    def detect_ocr(self, ctxt):
        """
        Sends an OCR request to the Google Cloud Vision API.
        Args:
            ctxt (str): The base64 encoded string of the image.
        Returns:
            The detected text annotations or None if no text is found.
        """
        return self.__google_ocr.detect_ocr(ctxt)

    def predict_images(self, imgs):
        """
        Predict the class of the given images.
        Args:
            imgs (list): List of images in numpy array format.
        Returns:
            List of predictions with class names and probabilities.
        """
        return self.__icon_classifier.predict_images(imgs)