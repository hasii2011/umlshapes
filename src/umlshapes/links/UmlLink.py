
from typing import Tuple
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from wx import Point
from wx import MemoryDC

from umlmodel.Link import Link

from umlshapes.lib.ogl import FORMAT_SIZE_TO_CONTENTS

from umlshapes.lib.ogl import LineShape
from umlshapes.lib.ogl import Shape

from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.UmlUtils import UmlUtils

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.links.LabelType import LabelType
from umlshapes.links.UmlLinkLabel import UmlLinkLabel
from umlshapes.links.eventhandlers.UmlAssociationLabelEventHandler import UmlAssociationLabelEventHandler

from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.mixins.PubSubMixin import PubSubMixin

from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint
from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPointType

from umlshapes.shapes.eventhandlers.UmlLineControlPointEventHandler import UmlLineControlPointEventHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.Common import TAB
from umlshapes.types.Common import EndPositions
from umlshapes.types.Common import NAME_IDX
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlPosition import UmlPositions

if TYPE_CHECKING:
    from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
    from umlshapes.ShapeTypes import LinkableUmlShape


class UmlLink(IdentifierMixin, LineShape, PubSubMixin):
    """
    Notice that the IdentifierMixin is placed before any Shape mixin.
    See Python left to right method resolution order (MRO)

    Some links may need the pubsub mixin so put it at the lowest level
    """
    def __init__(self, link: Link):

        LineShape.__init__(self)
        IdentifierMixin.__init__(self)
        PubSubMixin.__init__(self)

        self.linkLogger:   Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()

        self._link:     Link                = link
        self._linkName: UmlLinkLabel = cast(UmlLinkLabel, None)

        self.SetFormatMode(mode=FORMAT_SIZE_TO_CONTENTS)
        self.SetDraggable(True, recursive=True)

    @property
    def sourceShape(self) -> 'LinkableUmlShape':
        return self.GetFrom()

    @sourceShape.setter
    def sourceShape(self, shape: 'LinkableUmlShape'):
        self.SetFrom(shape)

    @property
    def destinationShape(self) -> 'LinkableUmlShape':
        return self.GetTo()

    @destinationShape.setter
    def destinationShape(self, shape: 'LinkableUmlShape'):
        self.SetTo(shape)

    @property
    def umlFrame(self) -> 'ClassDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'ClassDiagramFrame'):
        self.SetCanvas(frame)

    @property
    def modelLink(self) -> Link:
        return self._link

    @modelLink.setter
    def modelLink(self, link: Link):
        self._link = link

    @property
    def linkName(self) -> UmlLinkLabel:
        return self._linkName

    @linkName.setter
    def linkName(self, linkName: UmlLinkLabel):
        self._linkName = linkName

    @property
    def selected(self) -> bool:
        return self.Selected()

    @selected.setter
    def selected(self, select: bool):
        self.Select(select=select)

    @property
    def controlPositions(self) -> UmlPositions:
        """

        Returns:  The UmlPositions
        """
        umlPositions: UmlPositions = UmlPositions([])

        for cp in self._controlPoints:
            lineControlPoint: UmlLineControlPoint = cast(UmlLineControlPoint, cp)
            point: Point = lineControlPoint.point

            umlPosition: UmlPosition = UmlPosition(x=point.x, y=point.y)
            umlPositions.append(umlPosition)

        return umlPositions

    @property
    def endPositions(self) -> EndPositions:
        """
        Syntactic sugar around the .GetEnds() and .SetEnd() methods

        Returns: The EndPositions data class

        """

        #    fromX, fromY, toX, toY
        ends: Tuple[int, int, int, int] = self.GetEnds()

        return EndPositions(
            fromPosition=UmlPosition(x=ends[0], y=ends[1]),
            toPosition=UmlPosition(x=ends[2], y=ends[3])
        )

    @endPositions.setter
    def endPositions(self, endPoints: EndPositions):

        fromPosition: UmlPosition = endPoints.fromPosition
        toPosition:   UmlPosition = endPoints.toPosition

        self.SetEnds(x1=fromPosition.x, y1=fromPosition.y, x2=toPosition.x, y2=toPosition.y)

    @property
    def spline(self) -> bool:
        return self.IsSpline()

    @spline.setter
    def spline(self, spline: bool):
        self.SetSpline(spline)

    def toggleSpline(self):

        self.SetSpline(not self.IsSpline())

        frame = self.GetCanvas()
        frame.Refresh()
        # self._indicateDiagramModified()

    def setLinkEnds(self, fromPosition: UmlPosition, toPosition: UmlPosition):
        """
        Adjust the link ends
        Args:
            fromPosition:   The from position
            toPosition:     The to position
        """
        self.SetEnds(
            x1=fromPosition.x,
            y1=fromPosition.y,
            x2=toPosition.x,
            y2=toPosition.y
        )

    def addLineControlPoint(self, umlPosition: UmlPosition):
        """
        Add a line control point. For example to 'add a bend' or
        create an orthogonal line

        Args:
            umlPosition:  The UML x,y coordinates
        """
        self.InsertLineControlPoint(point=Point(x=umlPosition.x, y=umlPosition.y))

    def OnDraw(self, dc: MemoryDC):
        if self._linkName is None:
            self._linkName = self._createLinkName()
            self._setupLinkText(umlAssociationLabel=self._linkName)

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

    def _createLinkName(self) -> UmlLinkLabel:

        labelX, labelY = self.GetLabelPosition(position=NAME_IDX)
        return self._createLinkLabel(x=labelX, y=labelY, text=self.modelLink.name, labelType=LabelType.ASSOCIATION_NAME)

    def _createLinkLabel(self, x: int, y: int, text: str, labelType: LabelType) -> UmlLinkLabel:
        """

        Args:
            x:      The label x position
            y:      The label y position
            text:   The label text
            labelType: Determines if the label initially appears at the link start, end, or in the middle
        """

        assert text is not None, 'Developer error'

        umlAssociationLabel: UmlLinkLabel = UmlLinkLabel(label=text, labelType=labelType)

        umlAssociationLabel.position = UmlPosition(x=x, y=y)
        #
        # Maybe not necessary, but let's be consistent
        #
        self._children.append(umlAssociationLabel)
        self._setupLinkText(umlAssociationLabel)

        return umlAssociationLabel

    def _setupLinkText(self, umlAssociationLabel: UmlLinkLabel):
        """

        Args:
            umlAssociationLabel:
        """
        umlFrame: UmlFrame = self.GetCanvas()
        umlAssociationLabel.SetCanvas(umlFrame)
        umlAssociationLabel.parent = self

        diagram: UmlDiagram = umlFrame.umlDiagram
        diagram.AddShape(umlAssociationLabel)

        self._setupLinkTextEventHandler(umlAssociationLabel)

    def _setupLinkTextEventHandler(self, umlAssociationLabel: UmlLinkLabel):
        """

        Args:
            umlAssociationLabel:
        """
        eventHandler: UmlAssociationLabelEventHandler = UmlAssociationLabelEventHandler(previousEventHandler=umlAssociationLabel.GetEventHandler())

        eventHandler.SetShape(umlAssociationLabel)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine

        umlAssociationLabel.SetEventHandler(eventHandler)

    def __str__(self) -> str:
        srcShape: Shape = self.GetFrom()
        dstShape: Shape = self.GetTo()

        return f'UmlLink: {srcShape} {dstShape}'

    def __repr__(self) -> str:

        srcShape: IdentifierMixin = self.GetFrom()
        dstShape: IdentifierMixin = self.GetTo()
        sourceId: str   = srcShape.id
        dstId:    str   = dstShape.id

        readable: str = (
            f'{osLineSep}'
            f'{TAB}from: id: {sourceId:<35} {srcShape}{osLineSep}'
            f'{TAB}to    id: {dstId:<35} {dstShape}'
        )
        return readable
