#!/usr/bin/env python
from pathlib import Path

import pyautogui
from codeallybasic.Basic import Basic
from codeallybasic.Basic import RunResult
from codeallybasic.UnitTestBase import UnitTestBase
from pyautogui import click
from pyautogui import moveTo
from pyautogui import dragTo
from PIL.Image import Image

# Hmm why is this coming from here
from pymsgbox import alert


pyautogui.PAUSE = 0.5

DRAG_DURATION: float = 0.5
LEFT:          str   = 'left'
SHAPES_IMAGE_FILENAME:   str = f'testShapes.png'
VERIFICATION_IMAGE_PATH: str = f'/tmp/{SHAPES_IMAGE_FILENAME}'

# noinspection SpellCheckingInspection
GOLDEN_IMAGE_PACKAGE:   str = 'tests.uitests.goldenImages'

def makeAppActive():
    # Make UML Diagrammer Active
    moveTo(130, 110)
    click()

def pullDownViewMenu():
    # Pull down view menu
    click(220, 20, button=LEFT)

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

def takeCompletionScreenShot():

    cleanupImage: Path = Path(VERIFICATION_IMAGE_PATH)
    cleanupImage.unlink(missing_ok=True)
    doneImage: Image = pyautogui.screenshot(region=(18, 39, 1030, 730))

    doneImage.save(VERIFICATION_IMAGE_PATH)

def wasTestSuccessful() -> bool:
    answer: bool = False

    path: str = UnitTestBase.getFullyQualifiedResourceFileName(package=GOLDEN_IMAGE_PACKAGE, fileName=SHAPES_IMAGE_FILENAME)

    diffCmd: str = (
        'diff '
        f'{VERIFICATION_IMAGE_PATH} '
        f'{path}'
    )
    result: RunResult = Basic.runCommand(programToRun=diffCmd)
    if result.returnCode == 0:
        answer = True

    return answer


if __name__ == '__main__':

    makeAppActive()
    testActor()
    testUseCase()
    testNote()
    testText()
    testClass()
    takeCompletionScreenShot()

    success: bool = wasTestSuccessful()

    if success is True:
        title:   str = 'Success'
        message: str = 'You are a great programmer'
    else:
        title   = 'Failure'
        message = 'You have failed as a programmer'

    alert(text=message, title=title, button='OK')
