from uta.ModelManagement.VisionModel._GoogleOCR import _GoogleOCR
from uta.ModelManagement.VisionModel._IconClassifier import _IconClassifier


class _VisionModel:
    def __init__(self):
        """
        Initializes a VisionModel instance with ocr and icon classifier.
        """
        self.__google_ocr = _GoogleOCR()
        self.__icon_classifier = _IconClassifier()

    def detect_text_ocr(self, img_path):
        """
        Sends an OCR request to the Google Cloud Vision API.
        Args:
            img_path (str): Image file path.
        Returns:
            The detected text annotations or None if no text is found.
        """
        return self.__google_ocr.detect_text_ocr(img_path)

    def classify_icons(self, imgs):
        """
        Predict the class of the given icons images.
        Args:
            imgs (list): List of images in numpy array format.
        Returns:
            List of predictions with class names and probabilities.
        """
        return self.__icon_classifier.classify_icons(imgs)
