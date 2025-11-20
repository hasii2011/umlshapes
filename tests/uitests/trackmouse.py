#!/usr/bin/env python
from time import sleep

import pyautogui
print('Press Ctrl-C to quit.')

try:
    while True:
        x, y = pyautogui.position()
        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
        print(positionStr, end='')
        print('\b' * len(positionStr), end='', flush=True)
        sleep(1)
except KeyboardInterrupt:
    print('\n')
