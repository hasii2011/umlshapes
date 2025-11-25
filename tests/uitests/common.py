
from pathlib import Path

from pyautogui import moveTo
from pyautogui import click

DEMO_RUNNING_INDICATOR: Path = Path('/tmp/DemoRunning.txt')

LEFT:          str   = 'left'
DRAG_DURATION: float = 0.5

def isAppRunning() -> bool:
    answer: bool = False

    if DEMO_RUNNING_INDICATOR.exists() is True:
        answer = True

    return answer

def makeAppActive():
    # Make UML Diagrammer Active
    moveTo(130, 110)
    click()

def pullDownViewMenu():
    # Pull down view menu
    click(220, 20, button=LEFT)
