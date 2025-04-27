
from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutLink import PyutLink
from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType
from wx.lib.ogl import LineShape


class UmlLink(LineShape):

    def __init__(self, pyutLink: PyutLink):

        super().__init__()
        self.linkLogger: Logger = getLogger(__name__)

        self._pyutLink: PyutLink = pyutLink

        self.AddText(pyutLink.name)

        self.SetDraggable(True, recursive=True)

    @property
    def pyutLink(self) -> PyutLink:
        return self._pyutLink

    @pyutLink.setter
    def pyutLink(self, pyutLink: PyutLink):
        self._pyutLink = pyutLink

    def toggleSpline(self):

        self.SetSpline(not self.IsSpline())

        frame = self.GetCanvas()
        frame.Refresh()
        # self._indicateDiagramModified()
