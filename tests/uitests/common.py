
from pathlib import Path

from PIL import ImageGrab
from PIL.Image import Image

from pyautogui import moveTo
from pyautogui import click

DEMO_RUNNING_INDICATOR: Path = Path('/tmp/DemoRunning.txt')

# noinspection SpellCheckingInspection
GOLDEN_IMAGE_PACKAGE:   str = str('tests.uitests.goldenImages')

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

def takeCompletionScreenShot(imagePath: Path):

    imagePath.unlink(missing_ok=True)

    left:   int = 18
    top:    int = 39
    right:  int = 1030
    bottom: int = 730

    bbox = (left, top, right, bottom)

    # Capture the specified region
    screenshot: Image = ImageGrab.grab(bbox)
    screenshot.save(imagePath, 'png')
