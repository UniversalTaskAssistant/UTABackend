from uta.DataStructures import *
from uta.ModelManagement import ModelManager
from uta.ModelManagement.FMModel import _OpenAI
from uta.ModelManagement.VisionModel import _GoogleOCR, _IconClassifier, _VisionModel


def test_task():
    task = Task("1", "1", "Open Youtube")
    print(task)
    print(task.to_dict())

    new_task = {'task_id': "2", "user_id": "2", "task_description": "Close Youtube", "fake_attr": "abc"}
    task.load_from_dict(new_task)
    print(task.to_dict())

    action = {"Action": "Long Press", "Element": "19", "Description": "N/A", "Input Text": "N/A", "Reason": "N/A"}
    task.actions.append(action)
    print(task.to_dict())


def test_llmmodel():
    llm_model = _OpenAI()
    conversation = []
    while True:
        user_input = input()
        user_input = {'role': 'user', 'content': user_input}
        conversation.append(user_input)
        msg = llm_model.send_openai_conversation(conversation, printlog=True, runtime=True)
        print(msg)
        conversation.append(msg)


def test_googleocr():
    img_path = '../old_test_data/test/general/0.png'
    google_ocr = _GoogleOCR()
    img_data2 = google_ocr.detect_text_ocr(img_path, show=True, shrink_size=True)
    print(img_data2)


def test_model_manager():
    model_manager = ModelManager()
    conversation = []
    for i in range(2):
        user_input = input()
        user_input = {'role': 'user', 'content': user_input}
        conversation.append(user_input)
        msg = model_manager.send_fm_conversation(conversation, printlog=True, runtime=True)
        print(msg)
        conversation.append(msg)


if __name__ == '__main__':
    # test_task()
    # test_llmmodel()
    test_model_manager()