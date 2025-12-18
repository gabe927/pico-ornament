from context import AppContext
from utime import sleep
from modes import Modes


BRIGHTNESS_INCREMENT = 10
WIFI_CONN_ATTEMPTS = 3


### Setup ###

# initialize 
context = AppContext()

# attempt to connect to wifi
for i in range(WIFI_CONN_ATTEMPTS):
    if context.net.connect():
        break

# show wifi status on display
context.scroll.clear()
width = context.scroll.get_width()
height = context.scroll.get_height()
if context.net.is_connected:
    # once connected, show checkmark
    context.scroll.set_pixel(0, height-2, context.brightness.value)
    context.scroll.set_pixel(1, height-1, context.brightness.value)
    context.scroll.set_pixel(2, height-2, context.brightness.value)
    context.scroll.set_pixel(3, height-3, context.brightness.value)
    context.scroll.set_pixel(4, height-4, context.brightness.value)
else:
    # if not connected, show X
    context.scroll.set_pixel(0, height-3, context.brightness.value)
    context.scroll.set_pixel(0, height-1, context.brightness.value)
    context.scroll.set_pixel(1, height-2, context.brightness.value)
    context.scroll.set_pixel(2, height-3, context.brightness.value)
    context.scroll.set_pixel(2, height-1, context.brightness.value)
context.scroll.show()
sleep(2)


# recall/init mode
m = Modes(context)


### Functions ###

# use for detecting if button is being pressed and not held
buttons = {
    'A' : {
        'isPressed' : False,
        'pin'       : context.scroll.BUTTON_A
    },
    'B' : {
        'isPressed' : False,
        'pin'       : context.scroll.BUTTON_B
    },
    'X' : {
        'isPressed' : False,
        'pin'       : context.scroll.BUTTON_X
    },
    'Y' : {
        'isPressed' : False,
        'pin'       : context.scroll.BUTTON_Y
    }
}
def is_button_pressed(button):
    is_pressed = context.scroll.is_pressed(buttons[button]['pin'])
    return_bool = is_pressed and not buttons[button]['isPressed']
    buttons[button]['isPressed'] = is_pressed
    return return_bool


### Loop ###

while True:
    # run mode tick
    m.run_tick()

    # check if button is pushed

    # increase brightness on X
    if is_button_pressed('X'):
        print("X is pressed!")
        context.brightness.set_rel_value(BRIGHTNESS_INCREMENT)
    # decrease brightness on Y
    if is_button_pressed('Y'):
        print("Y is pressed!")
        context.brightness.set_rel_value(-BRIGHTNESS_INCREMENT)
    # TODO re-attempt wifi if disconnected (need to be careful not to block ticks too long)
    sleep(0.01)

context.net.led.off()