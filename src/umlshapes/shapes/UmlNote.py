
from logging import Logger
from logging import getLogger

from wx import Brush
from wx import Colour
from wx import MemoryDC

from umlshapes.lib.ogl import FORMAT_CENTRE_HORIZ
from umlshapes.lib.ogl import FORMAT_CENTRE_VERT
from umlshapes.lib.ogl import RectangleShape

from pyutmodelv2.PyutNote import PyutNote

from umlshapes.UmlUtils import UmlUtils

from umlshapes.links.UmlNoteLink import UmlNoteLink

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.mixins.TopLeftMixin import TopLeftMixin
from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.mixins.ControlPointMixin import ControlPointMixin

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.frames.UseCaseDiagramFrame import UseCaseDiagramFrame
from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame


class UmlNote(ControlPointMixin, IdentifierMixin, RectangleShape, TopLeftMixin):
    """
    This is an UML object that represents a UML note in diagrams.
    A note may be linked only with a basic link

    Notice that the IdentifierMixin is placed before any Shape mixin.
    See Python left to right method resolution order (MRO)

    """

    MARGIN: int = 10

    def __init__(self, pyutNote: PyutNote | None = None, size: UmlDimensions = None):
        """

        Args:
            pyutNote:   A PyutNote Object
            size:       An initial size that overrides the default
        """
        self._preferences: UmlPreferences = UmlPreferences()

        if pyutNote is None:
            self._pyutNote: PyutNote = PyutNote()
        else:
            self._pyutNote = pyutNote

        super().__init__(shape=self)

        if size is None:
            noteSize: UmlDimensions = self._preferences.noteDimensions
        else:
            noteSize = size

        ControlPointMixin.__init__(self, shape=self)
        IdentifierMixin.__init__(self)
        RectangleShape.__init__(self, w=noteSize.width, h=noteSize.height)
        TopLeftMixin.__init__(self, umlShape=self, width=noteSize.width, height=noteSize.height)

        self.logger: Logger = getLogger(__name__)
        self.SetBrush(Brush(Colour(255, 255, 230)))

        self.SetDraggable(drag=True)
        self.SetCentreResize(False)

        self.SetFont(UmlUtils.defaultFont())
        self.SetFormatMode(mode=FORMAT_CENTRE_HORIZ | FORMAT_CENTRE_VERT)

    @property
    def selected(self) -> bool:
        return self.Selected()

    @selected.setter
    def selected(self, select: bool):
        self.Select(select=select)

    @property
    def pyutNote(self):
        return self._pyutNote

    @pyutNote.setter
    def pyutNote(self, newNote: PyutNote):
        self._pyutNote = newNote

    @property
    def umlFrame(self) -> ClassDiagramFrame | UseCaseDiagramFrame | SequenceDiagramFrame:
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: ClassDiagramFrame | UseCaseDiagramFrame | SequenceDiagramFrame):
        self.SetCanvas(frame)

    def addLink(self, umlNoteLink: UmlNoteLink, umlClass: UmlClass):

        self.AddLine(line=umlNoteLink, other=umlClass)

    def OnDraw(self, dc: MemoryDC):
        """

        Args:
            dc:
        """
        super().OnDraw(dc)

        if self.Selected() is True:
            if self.Selected() is True:
                UmlUtils.drawSelectedRectangle(dc=dc, shape=self)

        w:     int = self.GetWidth()
        h:     int = self.GetHeight()
        baseX: int = self.GetX() - (w // 2)
        baseY: int = self.GetY() - (h // 2)

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

        x1:    int = baseX + w - UmlNote.MARGIN
        y1:    int = baseY
        x2:    int = baseX + w
        y2:    int = baseY + UmlNote.MARGIN

        # self.logger.info(f'Position: ({baseX},{baseY})  {w=} {x1=} {y1=} {x2=} {y2=}')
        dc.DrawLine(x1, y1, x2, y2)

    def __str__(self) -> str:
        pyutNote: PyutNote = self._pyutNote
        if pyutNote is None:
            return f'Anonymous Note'
        else:
            return f'{pyutNote.content}'

    def __repr__(self):

        return f'UmlNote - umlId: `{self.id}` modelId: {self.pyutNote.id}'
