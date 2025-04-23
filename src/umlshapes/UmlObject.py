
from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutActor import PyutActor
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutNote import PyutNote
from pyutmodelv2.PyutText import PyutText
from pyutmodelv2.PyutUseCase import PyutUseCase

from wx.lib.ogl import RectangleShape

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.types.Common import LeftCoordinate
from umlshapes.types.Common import ModelObject
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition


class UmlObject(RectangleShape):

    def __init__(self, modelObject: ModelObject = None, size: UmlDimensions = None):
        """

        Args:
            modelObject:  The data model object
        """
        self._preferences: UmlPreferences = UmlPreferences()

        if size is None:
            shapeSize: UmlDimensions = self._preferences.classDimensions
        else:
            shapeSize = size

        super().__init__(w=shapeSize.width, h=shapeSize.height)

        self.baseLogger:   Logger      = getLogger(__name__)
        self._modelObject: ModelObject = modelObject

    @property
    def pyutClass(self) -> PyutClass:
        assert isinstance(self._modelObject, PyutClass), 'Developer error.  Requesting a PyutClass'
        return self._modelObject

    @pyutClass.setter
    def pyutClass(self, modelObject: PyutClass):
        assert isinstance(self._modelObject, PyutClass), 'Developer error.  Setting a PyutClass'
        self._modelObject = modelObject

    @property
    def pyutNote(self) -> PyutNote:
        assert isinstance(self._modelObject, PyutNote), 'Developer error.  Requesting a PyutNote'
        return self._modelObject

    @pyutNote.setter
    def pyutNote(self, modelObject: PyutNote):
        assert isinstance(self._modelObject, PyutNote), 'Developer error.  Setting a PyutNote'
        self._modelObject = modelObject

    @property
    def pyutActor(self) -> PyutActor:
        assert isinstance(self._modelObject, PyutActor), 'Developer error.  Requesting a PyutActor'
        return self._modelObject

    @pyutActor.setter
    def pyutActor(self, modelObject: PyutActor):
        assert isinstance(self._modelObject, PyutActor), 'Developer error.  Setting a PyutActor'
        self._modelObject = modelObject

    @property
    def pyutText(self) -> PyutText:
        assert isinstance(self._modelObject, PyutText), 'Developer error.  Requesting a PyutText'
        return self._modelObject

    @pyutText.setter
    def pyutText(self, modelObject: PyutText):
        assert isinstance(self._modelObject, PyutText), 'Developer error.  Setting a PyutText'
        self._modelObject = modelObject

    @property
    def pyutUseCase(self) -> PyutUseCase:
        assert isinstance(self._modelObject, PyutUseCase), 'Developer error.  Requesting a PyutUseCase'
        return self._modelObject

    @pyutUseCase.setter
    def pyutUseCase(self, modelObject: PyutUseCase):
        assert isinstance(self._modelObject, PyutUseCase), 'Developer error.  Setting a PyutUseCase'
        self._modelObject = modelObject

    @property
    def size(self) -> UmlDimensions:
        return UmlDimensions(width=self.GetWidth(), height=self.GetHeight())

    @size.setter
    def size(self, newSize: UmlDimensions):

        self.SetWidth(round(newSize.width))
        self.SetHeight(round(newSize.height))

    @property
    def position(self) -> UmlPosition:
        return UmlPosition(x=self.GetX(), y=self.GetY())

    @position.setter
    def position(self, position: UmlPosition):

        self.SetX(round(position.x))
        self.SetY(round(position.y))

    @property
    def topLeft(self) -> LeftCoordinate:
        """
        This method necessary because ogl reports positions from the center of the shape
        Calculates the left top coordinate

        Returns:  An adjusted coordinate
        """

        x = self.GetX()                 # This points to the center of the rectangle
        y = self.GetY()                 # This points to the center of the rectangle

        width:  int = self.size.width
        height: int = self.size.height

        left: int = x - (width // 2)
        top:  int = y - (height // 2)

        return LeftCoordinate(x=round(left), y=round(top))
