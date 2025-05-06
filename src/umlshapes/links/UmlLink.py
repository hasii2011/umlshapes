
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Point

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
from umlshapes.shapes.eventhandlers.UmlAssociationLabelEventHandler import UmlAssociationLabelEventHandler

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
            self._setupAssociationLabel(umlAssociationLabel)

            self._associationName = umlAssociationLabel

        sourceCardinality: str = self._pyutLink.sourceCardinality
        if len(sourceCardinality) > 0:
            sourceCardinalityLabel: UmlAssociationLabel = UmlAssociationLabel(label=sourceCardinality)
            sourceCardinalityLabel.position = UmlPosition(x=x1, y=y1)
            self._setupAssociationLabel(sourceCardinalityLabel)

            self._sourceCardinality = sourceCardinalityLabel

        destinationCardinality: str = self.pyutLink.destinationCardinality
        if len(destinationCardinality) > 0:
            destinationCardinalityLabel: UmlAssociationLabel = UmlAssociationLabel(label=destinationCardinality)
            destinationCardinalityLabel.position = UmlPosition(x=x2, y=y2)
            self._setupAssociationLabel(destinationCardinalityLabel)

            self._sourceCardinality = destinationCardinalityLabel

    def OnDraw(self, dc: MemoryDC):

        super().OnDraw(dc=dc)
        self._associationName.Draw(dc=dc)

    def MakeControlPoints(self):
        """
        Override to use our custom points, so that when dragged we can see them
        """
        if self._canvas is not None and self._lineControlPoints is not None:

            firstPoint: Point = self._lineControlPoints[0]
            lastPoint:  Point = self._lineControlPoints[-1]

            umlControlPointSize: int = self._preferences.controlPointSize

            self._makeFromControlPoint(firstPoint, umlControlPointSize)
            self._makeIntermediateControlPoints(umlControlPointSize)
            self._makeToControlPoint(lastPoint, umlControlPointSize)

    def _makeFromControlPoint(self, firstPoint: Point, umlControlPointSize: int):
        """

        Args:
            firstPoint:             The coordinates
            umlControlPointSize:    The size, control points are square

        """
        control: UmlLineControlPoint = UmlLineControlPoint(
            self.GetCanvas(),
            umlLink=self,
            size=umlControlPointSize,
            x=firstPoint.x,
            y=firstPoint.y,
            controlPointType=CONTROL_POINT_ENDPOINT_FROM
        )
        control._point = firstPoint
        self._setupControlPoint(umlLineControlPoint=control)

    def _makeIntermediateControlPoints(self, umlControlPointSize: int):
        """

        Args:
            umlControlPointSize:    The size, control points are square

        """
        for point in self._lineControlPoints[1:-1]:
            control = UmlLineControlPoint(
                self._canvas,
                self,
                umlControlPointSize,
                point.x,
                point.y,
                controlPointType=CONTROL_POINT_LINE)

            control._point = point
            self._setupControlPoint(umlLineControlPoint=control)

    def _makeToControlPoint(self, lastPoint: Point, umlControlPointSize: int):
        """

        Args:
            lastPoint:              The coordinates
            umlControlPointSize:    The size, control points are square

        """
        control = UmlLineControlPoint(
            self._canvas,
            self, umlControlPointSize,
            lastPoint.x,
            lastPoint.y,
            controlPointType=CONTROL_POINT_ENDPOINT_TO)
        control._point = lastPoint
        self._setupControlPoint(umlLineControlPoint=control)

    def _setupControlPoint(self, umlLineControlPoint: UmlLineControlPoint):
        """

        Args:
            umlLineControlPoint: The victim

        """
        self._canvas.AddShape(umlLineControlPoint)
        self._controlPoints.append(umlLineControlPoint)
        self._addEventHandler(umlLineControlPoint=umlLineControlPoint)

    def _addEventHandler(self, umlLineControlPoint: UmlLineControlPoint):
        """

        Args:
            umlLineControlPoint: The victim

        """

        eventHandler: UmlControlPointEventHandler = UmlControlPointEventHandler()
        eventHandler.SetShape(umlLineControlPoint)
        eventHandler.SetPreviousHandler(umlLineControlPoint.GetEventHandler())

        umlLineControlPoint.SetEventHandler(eventHandler)

    def _setupAssociationLabel(self, umlAssociationLabel):
        """

        Args:
            umlAssociationLabel:
        """
        umlFrame: UmlFrame = self.GetCanvas()
        umlAssociationLabel.SetCanvas(umlFrame)

        diagram: UmlDiagram = umlFrame.umlDiagram
        diagram.AddShape(umlAssociationLabel)

        self._associateAssociationLabelEventHandler(umlAssociationLabel)

    def _associateAssociationLabelEventHandler(self, umlAssociationLabel: UmlAssociationLabel):
        """

        Args:
            umlAssociationLabel:

        """

        eventHandler: UmlAssociationLabelEventHandler = UmlAssociationLabelEventHandler()

        eventHandler.SetShape(umlAssociationLabel)
        eventHandler.SetPreviousHandler(umlAssociationLabel.GetEventHandler())

        umlAssociationLabel.SetEventHandler(eventHandler)
