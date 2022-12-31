import os
import time
import traceback
from threading import Thread

import paramiko

from common.helpers import Singleton
from common.logger import logger

ROUTER_IP = os.getenv('ROUTER_IP')
ROUTER_USER = os.getenv('ROUTER_USER')
ROUTER_PASSWORD = os.getenv('ROUTER_PASSWORD')
ROUTER_PORT = os.getenv('ROUTER_PORT')
ROUTER_REQUEST_TIMEOUT = float(os.getenv('ROUTER_REQUEST_TIMEOUT'))
ROUTER_REQUEST_INTERVAL = float(os.getenv('ROUTER_REQUEST_INTERVAL'))
PROBE_COUNT_LIMIT = float(os.getenv('PROBE_COUNT_LIMIT'))
BACKEND_STARTUP_DELAY = float(os.getenv('BACKEND_STARTUP_DELAY'))
LIGHT_ON = 'Світло є'
LIGHT_OFF = 'Світла немає'
BOT_TAG = '📢'
ADMIN_IDS = os.getenv('ADMIN_IDS').split(',')


#
# g_current_state = None
# g_is_masked = False
#

# class PingListener:
#     def notify(self, state):
#         # raise MethodNotImplemented('Not Implemented')
#         pass



class Pinger(Singleton, Thread):
    is_online = None
    masked = False
    _listeners = []

    # def __init__(self):
    #

    def add_listeners(self, *listeners):
        self._listeners.extend(listeners)

    def add_listener(self, listener):
        self._listeners.append(listener)

    def check_availability(self):
        logger.info(f"REQUESTING ROUTER {ROUTER_IP}...")

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
                result = self.check_availability()
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
                                # listener.notify(self.is_online)
                                listener(self.is_online)
                            # dump_event(current_state)
                            # notify_subscribers(current_state)
                        else:
                            logger.info('STATE HAS CHANGED! NOTIFICATIONS ARE DISABLED!')

                logger.info('CURRENT STATE (ONLINE): %s', self.is_online)
                logger.info('PING_INTERVAL: %s', ROUTER_REQUEST_INTERVAL)
                time.sleep(ROUTER_REQUEST_INTERVAL)

            except Exception as e:
                logger.error(f'GENERAL ERROR: {e}')
                logger.error(traceback.format_exc())