
from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from wx import Bitmap
from wx import MemoryDC
from wx import NullBitmap

from wx.lib.ogl import OGLInitialize

from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote

BITMAP_WIDTH:  int   = 800
BITMAP_HEIGHT: int   = 800
CENTER_X:      float = 523.5
CENTER_Y:      float = 307.5
CLASS_WIDTH:   float = 255.4
CLASS_HEIGHT:  float = 185.9
ACTOR_WIDTH:   float = 140.2
ACTOR_HEIGHT:  float = 220.8
NOTE_WIDTH:    float = 220.6
NOTE_HEIGHT:   float = 140.4


class TestShapeClipping(UnitTestBaseW):
    """
    Test drawing shapes after interactive float resizing and positioning to
    verify clipping regions and DC drawing calls succeed without TypeError.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        OGLInitialize()

    def tearDown(self):
        super().tearDown()

    def testUmlClassFloatResizeClipping(self):

        umlClass: UmlClass = UmlClass()
        self._resizeWithFloatsAndDraw(shape=umlClass, width=CLASS_WIDTH, height=CLASS_HEIGHT)

    def testUmlActorFloatResizeClipping(self):

        umlActor: UmlActor = UmlActor()
        self._resizeWithFloatsAndDraw(shape=umlActor, width=ACTOR_WIDTH, height=ACTOR_HEIGHT)

    def testUmlNoteFloatResizeClipping(self):

        umlNote: UmlNote = UmlNote()
        self._resizeWithFloatsAndDraw(shape=umlNote, width=NOTE_WIDTH, height=NOTE_HEIGHT)

    def _resizeWithFloatsAndDraw(self, shape: UmlClass | UmlActor | UmlNote, width: float, height: float):

        shape.SetX(CENTER_X)
        shape.SetY(CENTER_Y)
        shape.SetSize(width, height)

        self.assertIsInstance(shape.GetX(), float)
        self.assertIsInstance(shape.GetY(), float)
        self.assertIsInstance(shape.GetWidth(), float)
        self.assertIsInstance(shape.GetHeight(), float)

        bitmap: Bitmap   = Bitmap(BITMAP_WIDTH, BITMAP_HEIGHT)
        dc:     MemoryDC = MemoryDC(bitmap)
        shape.OnDraw(dc)
        dc.SelectObject(NullBitmap)


def suite() -> TestSuite:

    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestShapeClipping))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
