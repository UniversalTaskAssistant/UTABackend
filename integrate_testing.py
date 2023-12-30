from UTA import UTA
from DataStructures import *

import json
import time


def connect_to_emulator(uta):
    """
    Connect to emulator.
    """
    uta.system_connector.connect_adb_device()


def capture_ui_information(uta):
    """
    Captures the current UI and view hierarchy.
    Returns:
        screenshot, view hierarchy, and resolution.
    """
    screenshot = uta.system_connector.cap_screenshot()
    vh = uta.system_connector.cap_current_ui_hierarchy()
    ui_resize = uta.system_connector.get_device_resolution()
    return screenshot, vh, ui_resize


def get_app_lists(uta):
    excepted_related_apps = uta.system_connector.get_current_package_and_activity_name()['package_name']
    device_app_list = uta.system_connector.get_app_list_on_the_device()
    return excepted_related_apps, device_app_list


def launch_app(uta, rel_app):
    uta.system_connector.launch_app(rel_app)
    cur_app, _ = uta.system_connector.get_current_package_and_activity_name().values()
    if cur_app in rel_app:
        return True
    return False


def execute_ui_operation(uta, action, ui, show=False, waiting_time=2):
    """
    Executes a UI operation based on the recommended action.
    Args:
        action (dict): Action to be performed.
        ui: The UI object on which the action is to be performed.
        show (bool): Shows the operation if True.
        waiting_time (int): Time to wait after performing the action.
    Raises:
        ValueError: If an unexpected action is encountered.
    """
    element = ui.elements[action['Element']]
    if action['Action'] == 'Click':
        uta.system_connector.click_screen(ui, element, show)
    elif action['Action'] == 'Scroll Up':
        uta.system_connector.up_scroll_screen(ui, element, show)
    elif action['Action'] == 'Scroll Down':
        uta.system_connector.down_scroll_screen(ui, element, show)
    elif action['Action'] == 'Swipe Right':
        uta.system_connector.right_swipe_screen(ui, element, show)
    elif action['Action'] == 'Swipe Left':
        uta.system_connector.left_swipe_screen(ui, element, show)
    elif action['Action'] == 'Long Press':
        uta.system_connector.long_press_screen(ui, element, show)
    elif action['Action'] == 'Input':
        uta.system_connector.input_text(action['Input Text'])
    else:
        raise ValueError(f"No expected action returned from model, returned action: {action['Action']}")
    time.sleep(waiting_time)


def automate_task(uta, task, max_turn=100, clarify_max_turn=3, related_app_max_turn=3, debug=False,
                  except_apps=None, printlog=False, show_operation=False):
    """
    Main function to automate a given task, handling task decomposition, execution, and result storage.

    Args:
        task (str): The task description.
        max_turn (int, optional): Maximum iterations for task automation. Defaults to 100.
        clarify_max_turn (int, optional): Maximum iterations for task clarification. Defaults to 3.
        related_app_max_turn (int, optional): Maximum attempts to launch related apps. Defaults to 3.
        debug (bool, optional): Enables debug mode if set to True. Defaults to False.
        except_apps (list, optional): List of apps to exclude from task automation. Defaults to None.
        printlog (bool, optional): Enables detailed logging if set to True. Defaults to False.
        show_operation (bool, optional): Whether to visually show UI operations. Defaults to False.
    """
    # Initializes the task execution agents
    connect_to_emulator(uta)
    uta.initialize_agents()

    screenshot, vh, ui_resize = capture_ui_information(uta)
    ui_data = uta.process_ui(screenshot, vh, ui_resize)

    # Create a new original task object and increment task ID
    original_task = OriginalTask(f"{uta.user_id}-{uta.ori_task_postfix_id}", original_task=task)
    conversation = task
    clarifyed_result = {"Clear": "False", "Question": ""}

    # Loop for task clarification with user interaction
    while clarify_max_turn and clarifyed_result['Clear'] == "False":
        clarifyed_result = uta.clarify_task(conversation, printlog)
        original_task.append_clarifying_conversation(({'role': 'user', 'content': task},
                                                      {'role': 'assistant', 'content': clarifyed_result}))

        conversation = input(clarifyed_result)  # we send this to front and wait for answer
        clarify_max_turn -= 1
    original_task.set_attributes(clarifyed_task=clarifyed_result['content'])

    # Decompose and classify the task into sub-tasks
    task_class_tuple = uta.decompose_and_classify_tasks(task, printlog)
    for (clarifyed_task, task_class) in task_class_tuple:
        # Create a new autonomic task object and increment task ID
        new_task = AutonomicTask(f"{uta.user_id}-{uta.ori_task_postfix_id}-{uta.autonomic_task_postfix_id}",
                                 task=clarifyed_task, task_type=task_class)
        uta.autonomic_task_postfix_id += 1

        # Process task based on its classification
        if task_class == "General Inquiry":
            llm_response = uta.execute_inquiry_task(clarifyed_task)

            # Create an inquiry step and append it to the new task
            inquiry_step = InquiryStep(f"{uta.user_id}-{uta.ori_task_postfix_id}-{uta.autonomic_task_postfix_id}"
                                       f"-{uta.step_postfix_id}")
            inquiry_step.set_attributes(user_conversation={'role': 'user', 'content': clarifyed_task},
                                        llm_conversation={'role': 'assistant', 'content': llm_response})
            uta.step_postfix_id += 1

            new_task.append_step(inquiry_step)
            new_task.set_attributes(execution_result="Finish")
        else:
            # Loop for executing non-inquiry tasks
            for step_turn in range(max_turn):
                excepted_related_apps, device_app_list = get_app_lists(uta)
                relation, action, result = uta.automate_app_and_system_task(ui_data, clarifyed_task,
                                                                            excepted_related_apps, device_app_list,
                                                                                      except_apps=except_apps,
                                                                                      printlog=printlog)

                # Create a new automation step
                auto_mode_step = AutoModeStep(f"{uta.user_id}-{uta.ori_task_postfix_id}-{uta.autonomic_task_postfix_id}"
                                       f"-{uta.step_postfix_id}")  # Create a new step with the given step_id
                auto_mode_step.set_attributes(ui_data=ui_data, relation=relation, execution_result=result)

                # Check the recommended action and set attributes
                if action:
                    auto_mode_step.set_attributes(recommended_action=action)
                    if result == "Can go back, execute the back action.":
                        auto_mode_step.set_attributes(is_go_back=True)

                uta.step_postfix_id += 1

                new_task.append_step(auto_mode_step)

                if result in {"Enter next turn.", "Can go back, execute the back action."}:
                    execute_ui_operation(uta, action, ui_data, show_operation)
                    # Annotate UI operation for debugging
                    if debug:
                        auto_mode_step.annotate_ui_openation()
                elif result == "No related app can be found.":
                    new_task.set_attributes(execution_result="Failed")
                    break
                elif result == "Task is completed.":
                    new_task.set_attributes(execution_result="Finish")
                    break
                else:
                    launch = 0
                    for _ in range(related_app_max_turn):
                        if launch_app(uta, action.description):
                            launch = 1
                            break
                    if not launch:
                        excepted_related_apps.append(action.description)
                        new_task.set_attributes(execution_result="Failed")
                        break

            # Exceed the max_turn
            if new_task.execution_result != 'Finish':
                new_task.set_attributes(execution_result="Failed")

        original_task.append_autonomic_task(new_task)
        uta.user.append_user_task(original_task)

    # Store the user's task data in a local file or database
    uta.store_data_to_local(json.loads(str(uta.user)), f"result_user_{uta.user.user_id}")  # later should be
    # changed to database/server