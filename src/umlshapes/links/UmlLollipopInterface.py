
from typing import Optional

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutInterface import PyutInterface

from wx.lib.ogl import Shape

from umlshapes.frames.UmlClassDiagramFrame import UmlClassDiagramFrame


class UmlLollipopInterface(Shape):

    def __init__(self, pyutInterface: PyutInterface, canvas: Optional[UmlClassDiagramFrame]):

        self._pyutInterface: PyutInterface = pyutInterface

        super().__init__(canvas=canvas)
        self.logger: Logger = getLogger(__name__)

    @property
    def pyutInterface(self) -> PyutInterface:
        return self._pyutInterface

    @pyutInterface.setter
    def pyutInterface(self, pyutInterface: PyutInterface):
        self._pyutInterface = pyutInterface

    def _isSameName(self, other: 'UmlLollipopInterface') -> bool:

        ans: bool = False
        if self.pyutInterface.name == other.pyutInterface.name:
            ans = True
        return ans

    def _isSameId(self, other: 'UmlLollipopInterface'):

        ans: bool = False
        if self.GetId() == other.GetId():
            ans = True
        return ans

    def __repr__(self):

        strMe: str = f'UmlLollipopInterface - "{self._pyutInterface.name}"'
        return strMe

    def __eq__(self, other: object):

        if isinstance(other, UmlLollipopInterface):
            if self._isSameName(other) is True and self._isSameId(other) is True:
                return True
            else:
                return False
        else:
            return False

    def __hash__(self):
        return hash(self._pyutInterface.name) + hash(self.GetId())
