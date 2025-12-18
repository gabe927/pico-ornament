from utime import sleep
from picoscroll import PicoScroll, WIDTH, HEIGHT
from machine import Pin

scroll = PicoScroll()
brightness = 1

pin = Pin("LED", Pin.OUT)

while True:
    try:
        scroll.clear()
        if scroll.is_pressed(scroll.BUTTON_A):
            if brightness < 255:
                brightness += 1
                print(f"Brightness set to {brightness}")
        elif scroll.is_pressed(scroll.BUTTON_B):
            if brightness > 0:
                brightness -= 1
                print(f"Brightness set to {brightness}")
        for y in range(HEIGHT):
            for x in range(WIDTH):
                scroll.set_pixel(x, y, brightness)
        scroll.show()

        pin.toggle()

    except KeyboardInterrupt:
        break

    sleep(0.05)
pin.off()
print("Finished.")