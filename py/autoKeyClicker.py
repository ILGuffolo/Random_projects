from pynput.keyboard import Key, Controller
import keyboard as kb  # using module keyboard

#simulate key press

keyboard = Controller()

while True:  # making a loop
    if kb.is_pressed('s'):   # if key 's' is pressed
        keyboard.press(Key.down)
        keyboard.release(Key.down)
        
    elif kb.is_pressed('w'):
        keyboard.press(Key.up)
        keyboard.release(Key.up)
        
    elif kb.is_pressed('a'):
        keyboard.press(Key.left)
        keyboard.release(Key.left)
        
    elif kb.is_pressed('d'):
        keyboard.press(Key.right)
        keyboard.release(Key.right)
