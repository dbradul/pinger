import os
import paramiko
import time
import traceback
from threading import Thread

from common.helpers import Singleton
from common.logger import logger

ROUTER_IP = os.getenv('ROUTER_IP')
ROUTER_USER = os.getenv('ROUTER_USER')
ROUTER_PASSWORD = os.getenv('ROUTER_PASSWORD')
ROUTER_PORT = os.getenv('ROUTER_PORT')
ROUTER_REQUEST_TIMEOUT = float(os.getenv('ROUTER_REQUEST_TIMEOUT'))
ROUTER_REQUEST_INTERVAL = float(os.getenv('ROUTER_REQUEST_INTERVAL'))
PROBE_COUNT_LIMIT = float(os.getenv('PROBE_COUNT_LIMIT'))

LIGHT_ON = 'Світло є'
LIGHT_OFF = 'Світла немає'
BOT_TAG = '📢'


class Pinger(Singleton, Thread):
    is_online = None
    masked = False
    forced_state = None
    _listeners = []

    def add_listeners(self, *listeners):
        self._listeners.extend(listeners)

    def add_listener(self, listener):
        self.add_listeners(self, [listener])

    def get_current_state_info(self, bot=False):
        tag = BOT_TAG if bot else ""
        state_info = LIGHT_ON if self.is_online else LIGHT_OFF
        return f'{tag} {state_info}'

    def _check_availability(self):
        logger.info(f"REQUESTING ROUTER {ROUTER_IP}...")

        if self.forced_state is not None:
            logger.info(f"Forced state is returned: {self.forced_state}")
            return self.forced_state

        result = False
        client = None

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=ROUTER_IP,
                username=ROUTER_USER,
                password=ROUTER_PASSWORD,
                port=ROUTER_PORT,
                timeout=ROUTER_REQUEST_TIMEOUT,
                allow_agent=False
            )
            result = True
        except Exception as ex:
            logger.error(f"ROUTER GENERAL ERROR: {ex}")
        finally:
            if client:
                client.close()
        return result

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
                            logger.info('STATE HAS CHANGED! NOTIFYING SUBSCRIBERS!')
                            for listener in self._listeners:
                                current_state_info = self.get_current_state_info(bot=True)
                                listener(current_state_info)
                        else:
                            logger.info('STATE HAS CHANGED! NOTIFICATIONS ARE DISABLED!')

                logger.info('CURRENT STATE (ONLINE): %s', self.is_online)
                logger.info('PING_INTERVAL: %s', ROUTER_REQUEST_INTERVAL)
                time.sleep(ROUTER_REQUEST_INTERVAL)

            except Exception as e:
                logger.error(f'GENERAL ERROR: {e}')
                logger.error(traceback.format_exc())