import socket

import paramiko

from common.logger import logger


class RemoteHost:
    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout

    def is_online(self) -> bool:
        result = False
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))
            sock.close()
            result = True
        except Exception as ex:
            logger.error(f"REMOTE HOST CONNECTION ERROR: {ex}")
        finally:
            sock.close()
        return result


class SSHRemoteHost(RemoteHost):
    def __init__(self, host, port, user, password, timeout):
        super().__init__(host, port, timeout)
        # self.ssh_client = ssh_client
        self.user = user
        self.password = password

    def is_online(self) -> bool:
        result = False
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.host,
                username=self.user,
                password=self.password,
                port=self.port,
                timeout=self.timeout,
                allow_agent=False
            )
            result = True
        except Exception as ex:
            logger.error(f"REMOTE HOST CONNECTION ERROR: {ex}")
        finally:
            if client:
                client.close()
        return result
