from subprocess import Popen, DEVNULL
import requests
import time

class Ngrok:
    def __init__(self, binary, token, protocol, ip, port, region=None):
        self.binary = binary
        self.token = token
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.region = region
        
        self.process = None

    def is_running(self):
        return self.process is not None

    def start(self):
        if self.is_running():
            return

        command = [self.binary, self.protocol, "--authtoken", self.token]
        if self.region is not None:
            command += ["--region", self.region]
        self.process = Popen(command + [f"{self.ip}:{self.port}"], stdout=DEVNULL, stderr=DEVNULL)

        time.sleep(0.1)
        return self.get_public_url()

    def stop(self):
        if not self.is_running():
            return

        self.process.kill()
        self.process = None

    def get_public_url(self):
        if not self.is_running():
            return None

        t = time.time()
        while time.time() - t < 10:
            try:
                response = requests.get("http://127.0.0.1:4040/api/tunnels").json()["tunnels"]
                if response:
                    return response[0]["public_url"]
            except:
                pass
            time.sleep(0.1)
