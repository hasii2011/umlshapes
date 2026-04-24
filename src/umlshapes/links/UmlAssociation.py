
from typing import List
from typing import NewType
from typing import Tuple
from typing import cast

from logging import Logger
from logging import getLogger

from math import pi
from math import atan
from math import cos
from math import sin

from wx import DC
from wx import RED_PEN
from wx import BLUE_PEN
from wx import BLACK_PEN
from wx import RED_BRUSH
from wx import BLACK_BRUSH
from wx import WHITE_BRUSH

from wx import Point
from wx import Pen
from wx import MemoryDC

from umlmodel.Link import Link

from umlshapes.utils.ShapeAnalysis import LeftTopRectangleIndicator
from umlshapes.utils.ShapeAnalysis import RelativeRectangleResult
from umlshapes.UmlUtils import UmlUtils

from umlshapes.links.UmlLink import UmlLink
from umlshapes.links.LabelType import LabelType
from umlshapes.links.UmlLinkLabel import UmlLinkLabel

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.Common import NAME_IDX
from umlshapes.types.Common import Rectangle
from umlshapes.types.Common import SOURCE_CARDINALITY_IDX
from umlshapes.types.Common import DESTINATION_CARDINALITY_IDX
from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.types.UmlPosition import UmlPosition

SegmentPoint  = NewType('SegmentPoint',  Tuple[int, int])
Segments      = NewType('Segments',      List[SegmentPoint])

DiamondPoint    = NewType('DiamondPoint',  Tuple[int, int])
DiamondPoints   = NewType('DiamondPoints', List[DiamondPoint])

PI_6:         float = pi / 6


class UmlAssociation(UmlLink):

    clsDiamondSize: int = UmlPreferences().diamondSize

    def __init__(self, link: Link):

        super().__init__(link=link)

        self.associationLogger: Logger = getLogger(__name__)

        self._sourceCardinality:      UmlLinkLabel = cast(UmlLinkLabel, None)
        self._destinationCardinality: UmlLinkLabel = cast(UmlLinkLabel, None)

    @property
    def associationName(self) -> UmlLinkLabel:
        """
        Syntactic sugar around link name

        Returns:  The association name
        """
        return self._linkName

    @associationName.setter
    def associationName(self, newValue: UmlLinkLabel):
        self._linkName = newValue

    @property
    def sourceCardinality(self) -> UmlLinkLabel:
        return self._sourceCardinality

    @sourceCardinality.setter
    def sourceCardinality(self, newValue: UmlLinkLabel):
        self._sourceCardinality = newValue

    @property
    def destinationCardinality(self) -> UmlLinkLabel:
        return self._destinationCardinality

    @destinationCardinality.setter
    def destinationCardinality(self, newValue: UmlLinkLabel):
        self._destinationCardinality = newValue

    @property
    def segments(self) -> Segments:
        """
        The source anchor is the first, The destination anchor is the last.   The
        control points if any are the intermediate SegmentPoint

        Returns:  The segment points that describe the line, including the intermediate control points
        where the line bends
        """
        segments: Segments = Segments([])

        for cp in self.GetLineControlPoints():

            pt: Point = cast(Point, cp)
            sp: SegmentPoint = SegmentPoint((pt.x, pt.y))
            segments.append(sp)

        return segments

    def createAssociationLabels(self):

        self._linkName               = self._createLinkName()
        self._sourceCardinality      = self._createSourceCardinality()
        self._destinationCardinality = self._createDestinationCardinality()

    def smartPlaceLabels(self):
        """
        Association labels that appear either down from the other end or
        right from the other end are always obscured.
        See: https://github.com/hasii2011/umlshapes/issues/1

        """
        sourceShape      = self.sourceShape
        destinationShape = self.destinationShape

        rectangle1: Rectangle = sourceShape.rectangle
        rectangle2: Rectangle = destinationShape.rectangle

        result: RelativeRectangleResult = UmlUtils.computeRelativeRectanglePosition(rectangle1=rectangle1, rectangle2=rectangle2)

        if result.leftMostTopMostShape == LeftTopRectangleIndicator.RECTANGLE_1 and result.isOtherToBottom is True:
            self._repositionUmlLinkLabel(umlLinkLabel=self.destinationCardinality)
        elif result.leftMostTopMostShape == LeftTopRectangleIndicator.RECTANGLE_2 and result.isOtherToBottom is True:
            self._repositionUmlLinkLabel(umlLinkLabel=self.sourceCardinality)

    def OnDraw(self, dc: MemoryDC):

        super().OnDraw(dc=dc)

        if self._preferences.drawLabelMarker is True:
            labelX, labelY = self.GetLabelPosition(NAME_IDX)

            savePen: Pen = dc.GetPen()
            dc.SetPen(BLUE_PEN)
            dc.DrawText(f'({labelX},{labelY})', x=labelX, y=labelY)
            dc.DrawRectangle(labelX, labelY, 5, 5)
            dc.SetPen(savePen)

    def _repositionUmlLinkLabel(self, umlLinkLabel: UmlLinkLabel):
        """

        Args:
            umlLinkLabel:   The label to reposition
        """

        oldSourcePosition:         UmlPosition = umlLinkLabel.position
        associationLabelOffsetFix: int         = self._preferences.associationLabelOffsetFix
        newSourceCardinalityPosition: UmlPosition = UmlPosition(x=oldSourcePosition.x, y=oldSourcePosition.y - associationLabelOffsetFix)
        umlLinkLabel.position = newSourceCardinalityPosition

        deltaXY: DeltaXY = DeltaXY(
            deltaX=abs(newSourceCardinalityPosition.x - oldSourcePosition.x),
            deltaY=abs(newSourceCardinalityPosition.y - oldSourcePosition.y)
        )
        umlLinkLabel.linkDelta = deltaXY

    def _createDestinationCardinality(self) -> UmlLinkLabel:

        dstCardX, dstCardY = self.GetLabelPosition(position=DESTINATION_CARDINALITY_IDX)
        return self._createLinkLabel(x=dstCardX, y=dstCardY, text=self.modelLink.destinationCardinality, labelType=LabelType.DESTINATION_CARDINALITY)

    def _createSourceCardinality(self) -> UmlLinkLabel:

        srcCardX, srcCardY = self.GetLabelPosition(position=SOURCE_CARDINALITY_IDX)
        return self._createLinkLabel(x=srcCardX, y=srcCardY, text=self.modelLink.sourceCardinality, labelType=LabelType.SOURCE_CARDINALITY)

    def _drawDiamond(self, dc: DC, filled: bool = False):
        """
        Draw an arrow at the beginning of the line.

        Args:
            dc:     The device context
            filled: True if the diamond must be filled, False otherwise
        """
        line: Segments = self.segments

        # self.UmlAssociation.debug(f'{line=}')
        points: DiamondPoints = UmlAssociation.calculateDiamondPoints(lineSegments=line)
        # self.UmlAssociation.debug(f'{points:}')

        # noinspection PySimplifyBooleanCheck
        if self._selected is True:
            dc.SetPen(RED_PEN)
        else:
            dc.SetPen(BLACK_PEN)

        if filled:
            # noinspection PySimplifyBooleanCheck
            if self._selected is True:
                dc.SetBrush(RED_BRUSH)
            else:
                dc.SetBrush(BLACK_BRUSH)

        else:
            dc.SetBrush(WHITE_BRUSH)
        dc.DrawPolygon(points)
        dc.SetBrush(WHITE_BRUSH)

    @classmethod
    def calculateDiamondPoints(cls, lineSegments: Segments) -> DiamondPoints:
        """
        Made static so that we can unit test it;  Only instance variables needed
        are passed in

        Args:
            lineSegments:  The line where we are putting the diamondPoints

        Returns:  The diamond points that define the diamond polygon
        """
        x1, y1 = lineSegments[1]
        x2, y2 = lineSegments[0]
        a: int = x2 - x1
        b: int = y2 - y1
        if abs(a) < 0.01:  # vertical segment
            if b > 0:
                alpha: float = -pi / 2
            else:
                alpha = pi / 2
        else:
            if a == 0:
                if b > 0:
                    alpha = pi / 2
                else:
                    alpha = 3 * pi / 2
            else:
                alpha = atan(b/a)
        if a > 0:
            alpha += pi
        alpha1: float = alpha + PI_6
        alpha2: float = alpha - PI_6

        diamondPoints: DiamondPoints = DiamondPoints([])

        dp0: DiamondPoint = UmlAssociation.calculateDiamondPoint0(x2=x2, y2=y2, alpha1=alpha1)
        diamondPoints.append(dp0)

        diamondPoints.append(DiamondPoint((x2, y2)))

        dp2: DiamondPoint = UmlAssociation.calculateDiamondPoint2(x2=x2, y2=y2, alpha2=alpha2)
        diamondPoints.append(dp2)

        dp3: DiamondPoint = UmlAssociation.calculateDiamondPoint3(x2=x2, y2=y2, alpha=alpha)
        diamondPoints.append(dp3)

        return diamondPoints

    @classmethod
    def calculateDiamondPoint0(cls, x2: float, y2: float, alpha1: float) -> DiamondPoint:

        dpx0: float = x2 + UmlAssociation.clsDiamondSize * cos(alpha1)
        dpy0: float = y2 + UmlAssociation.clsDiamondSize * sin(alpha1)

        return DiamondPoint((round(dpx0), round(dpy0)))

    @classmethod
    def calculateDiamondPoint2(cls, x2: float, y2: float, alpha2: float) -> DiamondPoint:

        dpx2: float = x2 + UmlAssociation.clsDiamondSize * cos(alpha2)
        dpy2: float = y2 + UmlAssociation.clsDiamondSize * sin(alpha2)

        return DiamondPoint((round(dpx2), round(dpy2)))

    @classmethod
    def calculateDiamondPoint3(cls, x2: float, y2: float, alpha: float) -> DiamondPoint:

        dpx3: float = x2 + 2 * UmlAssociation.clsDiamondSize * cos(alpha)
        dpy3: float = y2 + 2 * UmlAssociation.clsDiamondSize * sin(alpha)

        return DiamondPoint((round(dpx3), round(dpy3)))

    def __repr__(self) -> str:
        return f'UmlAssociation {self.associationName} {super().__repr__()}'

    def __str__(self) -> str:
        return f'UmlAssociation {self.associationName} {super().__str__()}'
