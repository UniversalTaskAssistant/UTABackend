

class EventManager:
    def __init__(self):
        """
        Initializes the EventManager.
        Sets up a dictionary to keep track of event listeners.
        """
        self.listeners = {}

    def listen_to_event(self, event_name, listener):
        """
        Registers a listener for a specific event.
        Args:
            event_name (str): The name of the event to listen to.
            listener (callable): The callback function to be invoked when the event is triggered.
        """
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(listener)

    def trigger_event(self, event_name, **kwargs):
        """
        Triggers an event and calls all registered listeners for that event.
        Args:
            event_name (str): The name of the event to trigger.
            **kwargs: Keyword arguments to pass to the listener functions.
        Returns:
            The return value of the first listener, or None if no listeners are registered.
        """
        if event_name in self.listeners:
            for listener in self.listeners[event_name]:
                return listener(**kwargs)