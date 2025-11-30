#!/usr/bin/env python

from pathlib import Path

import pyautogui
from pyautogui import click
from pyautogui import dragTo

# Hmm why is this coming from here
from pymsgbox import alert

from codeallybasic.UnitTestBase import UnitTestBase

from tests.uitests.ExtendedBasic import EXIFTOOL
from tests.uitests.ExtendedBasic import ExtendedBasic
from tests.uitests.ExtendedBasic import VerifyStatus
from tests.uitests.common import GOLDEN_IMAGE_PACKAGE

from tests.uitests.common import LEFT
from tests.uitests.common import isAppRunning
from tests.uitests.common import makeAppActive
from tests.uitests.common import pullDownViewMenu
from tests.uitests.common import takeCompletionScreenShot

FIND_ME_IMAGE:           str = f'FindMe.png'
SHAPES_IMAGE_FILENAME:   str = f'testShapes.png'

VERIFICATION_IMAGE_PATH: Path = Path(f'/tmp/{SHAPES_IMAGE_FILENAME}')

def testActor():
    pullDownViewMenu()
    # Show Actor
    click(260, 290, button=LEFT)
    # Click Ok
    click(630, 440, button=LEFT)
    # Select Actor Shape
    click(166, 240)
    # Move the actor out of the way
    dragTo(950, 625, duration=DRAG_DURATION, button=LEFT)

def testUseCase():
    pullDownViewMenu()
    # Show Actor
    click(230, 270, button=LEFT)
    # Click Ok
    click(630, 440, button=LEFT)
    # Select Use Case
    click(166, 240, button=LEFT)

    dragTo(935, 500, duration=DRAG_DURATION, button=LEFT)

def testNote():
    pullDownViewMenu()
    # Show Note
    click(250, 250, button=LEFT)
    # Click Ok
    click(660, 500, button=LEFT)
    # Select Note
    click(200, 220, button=LEFT)
    dragTo(935, 180, duration=DRAG_DURATION, button=LEFT)

def testText():
    pullDownViewMenu()
    # Show Text
    click(220, 220, button=LEFT)
    # Click Ok
    click(666, 500, button=LEFT)
    # Select Text
    click(185, 220, button=LEFT)
    dragTo(940, 280, duration=DRAG_DURATION, button=LEFT)

def testClass():
    pullDownViewMenu()
    # Show Class
    click(235, 200, button=LEFT)
    # Select Class  Does not pop edit up dialog
    click(200, 230, button=LEFT)
    dragTo(645, 550, duration=DRAG_DURATION, button=LEFT)


def wasTestSuccessful() -> VerifyStatus:

    goldenImage: str          = UnitTestBase.getFullyQualifiedResourceFileName(package=GOLDEN_IMAGE_PACKAGE, fileName=SHAPES_IMAGE_FILENAME)
    answer:      VerifyStatus = ExtendedBasic.verifySameImage(goldenImage=Path(goldenImage), generatedImage=VERIFICATION_IMAGE_PATH)

    return answer


if __name__ == '__main__':

    pyautogui.PAUSE = 0.5
    DRAG_DURATION: float = 0.5

    if isAppRunning() is False:
        alert(text='The demo app is not running', title='Hey, bonehead', button='OK')
    else:
        makeAppActive()
        testActor()
        testUseCase()
        testNote()
        testText()
        testClass()
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
