from datetime import datetime

from common.models import History


class HistoryService:

    def dump_event(self, event_info: str):
        History.create(
            event_date=datetime.utcnow(),
            event_type=event_info
        )
