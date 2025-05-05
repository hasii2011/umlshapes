
from typing import cast

from logging import Logger
from logging import getLogger

from wx import RED

from wx import MemoryDC

from wx.lib.ogl import CONTROL_POINT_ENDPOINT_FROM
from wx.lib.ogl import CONTROL_POINT_ENDPOINT_TO
from wx.lib.ogl import CONTROL_POINT_LINE
from wx.lib.ogl import FORMAT_SIZE_TO_CONTENTS

from wx.lib.ogl import LineShape

from pyutmodelv2.PyutLink import PyutLink

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint
from umlshapes.shapes.eventhandlers.UmlControlPointEventHandler import UmlControlPointEventHandler

from umlshapes.shapes.eventhandlers.UmlTextEventHandler import UmlTextEventHandler

from umlshapes.types.UmlPosition import UmlPosition

ASSOCIATION_LABEL_MIDDLE: int = 0
ASSOCIATION_LABEL_START:  int = 1
ASSOCIATION_LABEL_END:    int = 2


class UmlLink(LineShape):

    def __init__(self, pyutLink: PyutLink):

        super().__init__()
        self.linkLogger:   Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()

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

    def MakeControlPoints(self):
        """

        """
        if self._canvas and self._lineControlPoints:
            first = self._lineControlPoints[0]
            last = self._lineControlPoints[-1]

            umlControlPointSize: int = self._preferences.controlPointSize

            control: UmlLineControlPoint = UmlLineControlPoint(
                self._canvas,
                self,
                umlControlPointSize,
                first[0],
                first[1],
                CONTROL_POINT_ENDPOINT_FROM
            )

            control._point = first
            self._canvas.AddShape(control)
            self._controlPoints.append(control)
            self._addEventHandler(umlControlPoint=control)

            for point in self._lineControlPoints[1:-1]:
                control = UmlLineControlPoint(self._canvas, self, umlControlPointSize, point[0], point[1], CONTROL_POINT_LINE)
                control._point = point
                self._canvas.AddShape(control)
                self._controlPoints.append(control)
                self._addEventHandler(umlControlPoint=control)

            control = UmlLineControlPoint(self._canvas, self, umlControlPointSize, last[0], last[1], CONTROL_POINT_ENDPOINT_TO)
            control._point = last
            self._canvas.AddShape(control)
            self._controlPoints.append(control)
            self._addEventHandler(umlControlPoint=control)

    def _addEventHandler(self, umlControlPoint: UmlLineControlPoint):

        eventHandler: UmlControlPointEventHandler = UmlControlPointEventHandler()
        eventHandler.SetShape(umlControlPoint)
        eventHandler.SetPreviousHandler(umlControlPoint.GetEventHandler())

        umlControlPoint.SetEventHandler(eventHandler)
