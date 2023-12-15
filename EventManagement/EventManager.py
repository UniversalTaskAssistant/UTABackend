

class EventManager:
    def __init__(self):
        self.listeners = {}

    def listen_to_event(self, event_name, listener):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(listener)

    def trigger_event(self, event_name, **kwargs):
        if event_name in self.listeners:
            for listener in self.listeners[event_name]:
                return listener(**kwargs)