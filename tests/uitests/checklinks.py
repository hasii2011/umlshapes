#!/usr/bin/env python

from pathlib import Path

import pyautogui
from codeallybasic.UnitTestBase import UnitTestBase
from pyautogui import click
from pyautogui import dragTo
from pymsgbox import alert

from tests.uitests.ExtendedBasic import EXIFTOOL
from tests.uitests.ExtendedBasic import ExtendedBasic
from tests.uitests.ExtendedBasic import VerifyStatus

from tests.uitests.common import DRAG_DURATION
from tests.uitests.common import GOLDEN_IMAGE_PACKAGE
from tests.uitests.common import LEFT
from tests.uitests.common import isAppRunning
from tests.uitests.common import makeAppActive
from tests.uitests.common import pullDownViewMenu
from tests.uitests.common import takeCompletionScreenShot

LINKS_IMAGE_FILENAME:   str = f'testLinks.png'

VERIFICATION_IMAGE_PATH: Path = Path(f'/tmp/{LINKS_IMAGE_FILENAME}')

def selectShapesToMove():
    click(40, 115)
    # Select the shapes and link
    dragTo(445, 515, duration=DRAG_DURATION, button=LEFT)

def testInterface():
    pullDownViewMenu()
    # Show Interface Link
    click(250, 50)
    # Start of selection
    selectShapesToMove()
    # Click on left most shape
    click(195, 240)
    # Move out of way
    dragTo(905, 485, duration=DRAG_DURATION, button=LEFT)

def testAggregation():
    pullDownViewMenu()
    # Show Aggregation Link
    click(245, 70)
    selectShapesToMove()
    # Click on left most shape
    click(170, 240)
    # Move out of way
    dragTo(885, 160, duration=DRAG_DURATION, button=LEFT)

def testComposition():
    pullDownViewMenu()
    # Show Aggregation Link
    click(250, 95)
    # Start of selection
    selectShapesToMove()
    # Click on left most shape
    click(170, 240)
    # Move out of way
    dragTo(640, 142, duration=DRAG_DURATION, button=LEFT)

def testInheritance():
    pullDownViewMenu()
    # Show Inheritance Link
    click(250, 125)
    selectShapesToMove()
    click(170, 240)
    # Move out of way
    dragTo(665, 485, duration=DRAG_DURATION, button=LEFT)

def testAssociation():
    pullDownViewMenu()
    # Show Association Link
    click(250, 145)
    selectShapesToMove()
    click(170, 240)
    # Move out of way
    dragTo(460, 485, duration=DRAG_DURATION, button=LEFT)

def testNoteLink():
    pullDownViewMenu()
    # Show Note Link
    click(250, 170)

def wasTestSuccessful() -> VerifyStatus:

    goldenImage: str          = UnitTestBase.getFullyQualifiedResourceFileName(package=GOLDEN_IMAGE_PACKAGE, fileName=LINKS_IMAGE_FILENAME)
    answer:      VerifyStatus = ExtendedBasic.verifySameImage(goldenImage=Path(goldenImage), generatedImage=VERIFICATION_IMAGE_PATH)

    return answer

if __name__ == '__main__':

    pyautogui.PAUSE = 0.5
    pyautogui.FAILSAFE = True

    if isAppRunning() is False:
        alert(text='The demo app is not running', title='Hey, bonehead', button='OK')
    else:
        makeAppActive()
        testInterface()
        testAggregation()
        testComposition()
        testInheritance()
        testAssociation()
        testNoteLink()

        takeCompletionScreenShot(imagePath=VERIFICATION_IMAGE_PATH)

        success: VerifyStatus = wasTestSuccessful()

        if success == VerifyStatus.SUCCESS:
            title:   str = 'Success'
            message: str = 'You are a great programmer'
        elif success == VerifyStatus.FAIL:
            title   = 'Failure'
            message = 'You have failed as a programmer'
        elif success == VerifyStatus.CANNOT_VERIFY:
            title   = 'Cannot verify tooling is messing'
            message = f'{EXIFTOOL} must be missing'
        else:
            assert False, 'Developer error'

        alert(text=message, title=title, button='OK')
