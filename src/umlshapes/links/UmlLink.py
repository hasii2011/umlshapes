
from typing import List
from typing import Tuple
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from wx import Point
from wx import MemoryDC

from wx.lib.ogl import FORMAT_SIZE_TO_CONTENTS

from wx.lib.ogl import LineShape
from wx.lib.ogl import Shape

from pyutmodelv2.PyutLink import PyutLink

from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.UmlUtils import UmlUtils

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.mixins.IDMixin import IDMixin

from umlshapes.links.LabelType import LabelType
from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.links.eventhandlers.UmlAssociationLabelEventHandler import UmlAssociationLabelEventHandler

from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint
from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPointType

from umlshapes.shapes.eventhandlers.UmlLineControlPointEventHandler import UmlLineControlPointEventHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.Common import EndPoints
from umlshapes.types.Common import NAME_IDX
from umlshapes.types.Common import TAB
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame


class UmlLink(LineShape, IDMixin):

    def __init__(self, pyutLink: PyutLink):

        LineShape.__init__(self)
        IDMixin.__init__(self, umlShape=self)

        self.linkLogger:   Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()

        self._pyutLink: PyutLink            = pyutLink
        self._linkName: UmlAssociationLabel = cast(UmlAssociationLabel, None)

        self.SetFormatMode(mode=FORMAT_SIZE_TO_CONTENTS)
        self.SetDraggable(True, recursive=True)

    @property
    def umlFrame(self) -> 'ClassDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'ClassDiagramFrame'):
        self.SetCanvas(frame)

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

    @property
    def endPoints(self) -> EndPoints:
        """
        Syntactic sugar around the .GetEnds() and .SetEnd() methods
        Returns:
        """

        #    fromX, fromY, toX, toY
        ends: Tuple[int, int, int, int] = self.GetEnds()

        return EndPoints(
            fromPosition=UmlPosition(x=ends[0], y=ends[1]),
            toPosition=UmlPosition(x=ends[2], y=ends[3])
        )

    @endPoints.setter
    def endPoints(self, endPoints: EndPoints):

        fromPosition: UmlPosition = endPoints.fromPosition
        toPosition:   UmlPosition = endPoints.toPosition

        self.SetEnds(x1=fromPosition.x, y1=fromPosition.y, x2=toPosition.x, y2=toPosition.y)

    @property
    def spline(self) -> bool:
        return self.IsSpline()

    @spline.setter
    def spline(self, spline: bool):
        self.SetSensitivityFilter(spline)

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
        These are really line control points
        """
        if self._canvas is not None and self._lineControlPoints is not None:

            firstPoint: Point = self._lineControlPoints[0]
            lastPoint:  Point = self._lineControlPoints[-1]

            self._makeLineControlPoint(point=firstPoint, controlPointType=UmlLineControlPointType.FROM_ENDPOINT)
            self._makeIntermediateControlPoints()
            self._makeLineControlPoint(point=lastPoint, controlPointType=UmlLineControlPointType.TO_ENDPOINT)

    def Draggable(self):
        """
        Override base behavior
        Line is not draggable.

        :note: This is really to distinguish between lines and other images.
         For lines we want to pass drag to canvas, since lines tend to prevent
         dragging on a canvas (they get in the way.)

        """
        return True

    def _makeIntermediateControlPoints(self):
        """

        """
        for point in self._lineControlPoints[1:-1]:
            self._makeLineControlPoint(point=point, controlPointType=UmlLineControlPointType.LINE_POINT)

    def _makeLineControlPoint(self, point: Point, controlPointType: UmlLineControlPointType):
        """
        Makes a specific type of line control point and ensures it appears on the UML
        frame

        Args:
            point:              Where
            controlPointType:   Type

        """

        umlControlPointSize: int = self._preferences.controlPointSize

        control = UmlLineControlPoint(
            umlFrame=self._canvas,
            umlLink=self,
            controlPointType=controlPointType,
            size=umlControlPointSize,
            x=point.x,
            y=point.y,
        )

        control._point = point
        self._setupLineControlPoint(umlLineControlPoint=control)

    def _setupLineControlPoint(self, umlLineControlPoint: UmlLineControlPoint):
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
