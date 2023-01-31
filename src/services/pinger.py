import os
import time
import traceback
from threading import Thread
from typing import List

from common.logger import logger
from common.remote_host import RemoteHost
from services import PingerListener

ROUTER_REQUEST_INTERVAL = float(os.getenv('ROUTER_REQUEST_INTERVAL'))
PROBE_COUNT_LIMIT = float(os.getenv('PROBE_COUNT_LIMIT'))

LIGHT_ON = 'Світло є'
LIGHT_OFF = 'Світла немає'
BOT_TAG = '📢'


class Pinger(Thread):
    is_online: bool = None
    masked: bool = False
    forced_state: bool = None
    _listeners: List[PingerListener] = []

    def __init__(self, remote_host: RemoteHost, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remote_host = remote_host

    # def add_listeners(self, *listeners: List[PingerListener]):
    def add_listeners(self, *listeners):
        self._listeners.extend(listeners)

    def add_listener(self, listener: PingerListener):
        self.add_listeners(listener)

    def get_current_state_info(self, bot=False):
        tag = BOT_TAG if bot else ""
        state_info = LIGHT_ON if self.is_online else LIGHT_OFF
        return f'{tag} {state_info}'

    def _check_availability(self):
        if self.forced_state is not None:
            logger.info(f"Forced state is returned: {self.forced_state}")
            return self.forced_state
        logger.info(f"REQUESTING ROUTER {self.remote_host.host}...")
        return self.remote_host.is_online()

    def run(self):
        probe_count = 0
        while True:
            try:
                result = self._check_availability()
                if self.is_online is None:
                    self.is_online = result
                else:
                    if self.is_online != result:
                        probe_count += 1
                    else:
                        probe_count = 0

                    if probe_count == PROBE_COUNT_LIMIT:
                        probe_count = 0
                        self.is_online = result
                        if not self.masked:
                            logger.info('STATE HAS CHANGED! NOTIFYING LISTENERS!')
                            for listener in self._listeners:
                                current_state_info = self.get_current_state_info(bot=True)
                                listener.on_state_change(current_state_info)
                        else:
                            logger.info('STATE HAS CHANGED! NOTIFICATIONS ARE DISABLED!')

                logger.info('CURRENT STATE (ONLINE): %s', self.is_online)
                logger.info('PING_INTERVAL: %s', ROUTER_REQUEST_INTERVAL)
                time.sleep(ROUTER_REQUEST_INTERVAL)

            except Exception as e:
                logger.error(f'GENERAL ERROR: {e}')
                logger.error(traceback.format_exc())