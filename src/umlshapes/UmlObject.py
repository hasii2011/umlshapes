
from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutObject import PyutObject
from wx.lib.ogl import RectangleShape


class UmlObject(RectangleShape):

    def __init__(self, pyutObject: PyutObject = None, width: int = 0, height: int = 0):
        """

        Args:
            pyutObject:  The data model object
            width:       width of the UML Shape
            height:      height of the UML Shape
        """

        self.logger: Logger = getLogger(__name__)

        super().__init__(w=width, h=height)

        self._pyutObject: PyutObject | None = pyutObject

    @property
    def pyutObject(self):
        return self._pyutObject

    @pyutObject.setter
    def pyutObject(self, pyutObject: PyutObject):
        self._pyutObject = pyutObject
