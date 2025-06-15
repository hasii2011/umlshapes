
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from wx import Point
from wx import MemoryDC

from wx.lib.ogl import CONTROL_POINT_ENDPOINT_FROM
from wx.lib.ogl import CONTROL_POINT_ENDPOINT_TO
from wx.lib.ogl import CONTROL_POINT_LINE
from wx.lib.ogl import FORMAT_SIZE_TO_CONTENTS

from wx.lib.ogl import LineShape
from wx.lib.ogl import Shape

from pyutmodelv2.PyutLink import PyutLink

from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.UmlUtils import UmlUtils
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.links.LabelType import LabelType
from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel

from umlshapes.links.eventhandlers.UmlAssociationLabelEventHandler import UmlAssociationLabelEventHandler

from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint

from umlshapes.shapes.eventhandlers.UmlLineControlPointEventHandler import UmlLineControlPointEventHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.Common import NAME_IDX
from umlshapes.types.Common import TAB
from umlshapes.types.UmlPosition import UmlPosition


class UmlLink(LineShape):

    def __init__(self, pyutLink: PyutLink):

        super().__init__()
        self.linkLogger:   Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()

        self._pyutLink: PyutLink            = pyutLink
        self._linkName: UmlAssociationLabel = cast(UmlAssociationLabel, None)

        self.SetFormatMode(mode=FORMAT_SIZE_TO_CONTENTS)
        self.SetDraggable(True, recursive=True)

    @property
    def controlPoints(self) -> List[UmlLineControlPoint]:
        return self._controlPoints

    @property
    def pyutLink(self) -> PyutLink:
        return self._pyutLink

    @pyutLink.setter
    def pyutLink(self, pyutLink: PyutLink):
        self._pyutLink = pyutLink

    @property
    def linkName(self) -> UmlAssociationLabel:
        return self._linkName

    @linkName.setter
    def linkName(self, linkName: UmlAssociationLabel):
        self._linkName = linkName

    @property
    def selected(self) -> bool:
        return self.Selected()

    @selected.setter
    def selected(self, select: bool):
        self.Select(select=select)

    def toggleSpline(self):

        self.SetSpline(not self.IsSpline())

        frame = self.GetCanvas()
        frame.Refresh()
        # self._indicateDiagramModified()

    def OnDraw(self, dc: MemoryDC):
        if self._linkName is None:
            self._linkName = self._createLinkName()
            self._setupAssociationLabel(umlAssociationLabel=self._linkName)

        if self.Selected() is True:
            self.SetPen(UmlUtils.redSolidPen())
        else:
            self.SetPen(UmlUtils.blackSolidPen())

        super().OnDraw(dc=dc)

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

        eventHandler: UmlLineControlPointEventHandler = UmlLineControlPointEventHandler()
        eventHandler.SetShape(umlLineControlPoint)
        eventHandler.SetPreviousHandler(umlLineControlPoint.GetEventHandler())

        umlLineControlPoint.SetEventHandler(eventHandler)

    def _createLinkName(self) -> UmlAssociationLabel:

        labelX, labelY = self.GetLabelPosition(position=NAME_IDX)
        return self._createAssociationLabel(x=labelX, y=labelY, text=self.pyutLink.name, labelType=LabelType.ASSOCIATION_NAME)

    def _createAssociationLabel(self, x: int, y: int, text: str, labelType: LabelType) -> UmlAssociationLabel:

        assert text is not None, 'Developer error'

        umlAssociationLabel: UmlAssociationLabel = UmlAssociationLabel(label=text, labelType=labelType)

        umlAssociationLabel.position = UmlPosition(x=x, y=y)
        self._setupAssociationLabel(umlAssociationLabel)

        return umlAssociationLabel

    def _setupAssociationLabel(self, umlAssociationLabel):
        """

        Args:
            umlAssociationLabel:
        """
        umlFrame: UmlFrame = self.GetCanvas()
        umlAssociationLabel.SetCanvas(umlFrame)
        umlAssociationLabel.parent = self

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

    def __str__(self) -> str:
        srcShape: Shape = self.GetFrom()
        dstShape: Shape = self.GetTo()

        return f'UmlLink: {srcShape} {dstShape}'

    def __repr__(self) -> str:

        srcShape: Shape = self.GetFrom()
        dstShape: Shape = self.GetTo()
        sourceId: int   = srcShape.GetId()
        dstId:    int   = dstShape.GetId()

        readable: str = (
            f'{osLineSep}'
            f'{TAB}from: id: {sourceId:<35} {srcShape}{osLineSep}'
            f'{TAB}to    id: {dstId:<35} {dstShape}'
        )
        return readable
