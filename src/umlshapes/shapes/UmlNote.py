
from logging import Logger
from logging import getLogger

from wx import Brush
from wx import Colour


from pyutmodelv2.PyutNote import PyutNote

from wx.lib.ogl import RectangleShape

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.shapes.ControlPointMixin import ControlPointMixin


class UmlNote(ControlPointMixin, RectangleShape):
    """
    This is an UML object that represents a UML note in diagrams.
    A note may be linked with all links except Inheritance and Interface.
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

    @property
    def pyutNote(self):
        return self._pyutNote

    @pyutNote.setter
    def pyutNote(self, newNote: PyutNote):
        self._pyutNote = newNote
