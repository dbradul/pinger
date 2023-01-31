from services.contact import ContactService
from services.history import HistoryService


class PingerListener:
    def __init__(self, contact_service: ContactService, history_service: HistoryService):
        self._contact_service = contact_service
        self._history_service = history_service

    def on_state_change(self, new_state: str):
        self._contact_service.notify_subscribers(new_state)
        self._history_service.dump_event(new_state)
