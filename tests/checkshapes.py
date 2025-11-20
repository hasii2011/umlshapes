#!/usr/bin/env python

import pyautogui
from pyautogui import click
from pyautogui import moveTo
from pyautogui import dragTo

pyautogui.PAUSE=2.0
DRAG_DURATION: float = 2.0
LEFT: str = 'left'

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
    click(274, 300, button=LEFT)
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
    click(200, 250, button=LEFT)

    dragTo(935, 500, duration=DRAG_DURATION, button=LEFT)


makeAppActive()
testActor()
testUseCase()
