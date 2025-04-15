
from logging import Logger
from logging import getLogger

from wx import Brush
from wx import Colour
from wx import MemoryDC

from wx.lib.ogl import RectangleShape

from pyutmodelv2.PyutNote import PyutNote

from umlshapes.UmlUtils import UmlUtils
from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.shapes.ControlPointMixin import ControlPointMixin


class UmlNote(ControlPointMixin, RectangleShape):
    """
    This is an UML object that represents a UML note in diagrams.
    A note may be linked only with a basic link
    """

    MARGIN: int = 10

    def __init__(self, pyutNote: PyutNote = None, width: int = 0, height: int = 0):
        """

        Args:
            pyutNote:   A PyutNote Object
            width:      Default width override
            height:     Default height override
        """
        self._preferences: UmlPreferences = UmlPreferences()

        if pyutNote is None:
            self._pyutNote: PyutNote = PyutNote()
        else:
            self._pyutNote = pyutNote

        super().__init__(shape=self)
        RectangleShape.__init__(self, w=width, h=height)

        if width == 0:
            self._width: int = self._preferences.noteDimensions.width
        else:
            self._width = width

        if height == 0:
            self._height: int = self._preferences.noteDimensions.height
        else:
            self._height = height

        self.logger: Logger = getLogger(__name__)
        self.SetBrush(Brush(Colour(255, 255, 230)))

        self.SetDraggable(drag=True)

        self.SetFont(UmlUtils.defaultFont())

    @property
    def pyutNote(self):
        return self._pyutNote

    @pyutNote.setter
    def pyutNote(self, newNote: PyutNote):
        self._pyutNote = newNote

    def OnDraw(self, dc: MemoryDC):
        """

        Args:
            dc:
        """
        try:
            super().OnDraw(dc)
        except (ValueError, Exception) as e:
            # Work around a bug where width & height sometimes become a float
            self.logger.warning(f'Bug workaround !!! {e}')

            self.SetWidth(round(self.GetWidth()))
            self.SetHeight(round(self.GetHeight()))
            super().OnDraw(dc)

        if self.Selected() is True:
            if self.Selected() is True:
                UmlUtils.drawSelectedRectangle(dc=dc, shape=self)

        w:     int = round(self.GetWidth())
        h:     int = round(self.GetHeight())
        baseX: int = round(self.GetX()) - (w // 2)
        baseY: int = round(self.GetY()) - (h // 2)

        self._drawNoteNotch(dc, w=w, baseX=baseX, baseY=baseY)

        try:
            noteContent = self.pyutNote.content
            lines = UmlUtils.lineSplitter(noteContent, dc, w - 2 * UmlNote.MARGIN)
        except (ValueError, Exception) as e:
            self.logger.error(f"Unable to display note - {e}")
            return

        x = baseX + UmlNote.MARGIN
        y = baseY + UmlNote.MARGIN

        for line in range(len(lines)):
            dc.DrawText(lines[line], x, y + line * (dc.GetCharHeight() + 5))

    def _drawNoteNotch(self, dc: MemoryDC, w: int, baseX: int, baseY: int):
        """
        Need the notch
        Args:
            dc:
        """
        # w:     int = round(self.GetWidth())
        # h:     int = round(self.GetHeight())
        # baseX: int = round(self.GetX()) - (w // 2)
        # baseY: int = round(self.GetY()) - (h // 2)
        x1:    int = baseX + w - UmlNote.MARGIN
        y1:    int = baseY
        x2:    int = baseX + w
        y2:    int = baseY + UmlNote.MARGIN

        # self.logger.info(f'Position: ({baseX},{baseY})  {w=} {x1=} {y1=} {x2=} {y2=}')
        dc.DrawLine(x1, y1, x2, y2)
