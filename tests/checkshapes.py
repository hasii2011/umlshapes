#!/usr/bin/env python

import pyautogui
from pyautogui import click
from pyautogui import moveTo
from pyautogui import dragTo

pyautogui.PAUSE=0.5
DRAG_DURATION: float = 1.0
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

makeAppActive()
testActor()
testUseCase()
testNote()
testText()
