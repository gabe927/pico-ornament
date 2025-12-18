import network
import secrets
from machine import Pin
from utime import sleep

class Networking:
    def __init__(self) -> None:
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        # use the pico LED for wifi status
        self.led = Pin("LED", Pin.OUT)

    def connect(self, timeout=10) -> bool:
        # attempt to connect to wifi
        if not self.wlan.isconnected():
            print('Connecting to network...')
            self.wlan.connect(secrets.SSID, secrets.PASSWORD)

        # check every 1 second if connected for *timeout* time
        for i in range(timeout):
            self.led.toggle()
            if self.wlan.isconnected():
                print(f'Connected! IP: {self.wlan.ifconfig()[0]}')
                self.led.on()
                sleep(1)
                return True
            sleep(1)
        else:
            print('Failed to connect.')
            self.led.off()
            return False
    
    @property
    def is_connected(self) -> bool:
        return self.wlan.isconnected()