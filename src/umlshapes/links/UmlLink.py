
from typing import cast

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutLink import PyutLink

from wx import MemoryDC
from wx import RED

from wx.lib.ogl import FORMAT_SIZE_TO_CONTENTS
from wx.lib.ogl import LineShape

from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.shapes.eventhandlers.UmlTextEventHandler import UmlTextEventHandler
from umlshapes.types.UmlPosition import UmlPosition

ASSOCIATION_LABEL_MIDDLE: int = 0
ASSOCIATION_LABEL_START:  int = 1
ASSOCIATION_LABEL_END:    int = 2


class UmlLink(LineShape):

    def __init__(self, pyutLink: PyutLink):

        super().__init__()
        self.linkLogger: Logger = getLogger(__name__)

        self._pyutLink: PyutLink = pyutLink

        self._associationName:        UmlAssociationLabel = cast(UmlAssociationLabel, None)
        self._sourceCardinality:      UmlAssociationLabel = cast(UmlAssociationLabel, None)
        self._destinationCardinality: UmlAssociationLabel = cast(UmlAssociationLabel, None)

        self.SetFormatMode(mode=FORMAT_SIZE_TO_CONTENTS)
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

    def createAssociationLabels(self):

        x1, y1, x2, y2 = self.FindLineEndPoints()

        labelX, labelY = self.GetLabelPosition(position=ASSOCIATION_LABEL_MIDDLE)

        associationName: str = self.pyutLink.name
        if len(associationName) > 0:
            umlAssociationLabel: UmlAssociationLabel = UmlAssociationLabel(label=associationName)
            umlAssociationLabel.position = UmlPosition(x=labelX, y=labelY)

            umlFrame: UmlFrame = self.GetCanvas()
            umlAssociationLabel.SetCanvas(umlFrame)

            diagram: UmlDiagram = umlFrame.umlDiagram

            diagram.AddShape(umlAssociationLabel)

            eventHandler: UmlTextEventHandler = UmlTextEventHandler(moveColor=RED)
            eventHandler.SetShape(umlAssociationLabel)
            eventHandler.SetPreviousHandler(umlAssociationLabel.GetEventHandler())

            umlAssociationLabel.SetEventHandler(eventHandler)

            self._associationName = umlAssociationLabel

    def OnDraw(self, dc: MemoryDC):

        super().OnDraw(dc=dc)
        self._associationName.Draw(dc=dc)
