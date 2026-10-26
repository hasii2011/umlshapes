
from typing import Optional
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import BLACK
from wx import MemoryDC
from wx import Pen
from wx import Point
from wx import Size
from wx import TRANSPARENT_BRUSH

from umlshapes.lib.ogl import ControlPoint
from umlshapes.lib.ogl import RectangleShape

from umlshapes.mixins.ControlPointMixin import ControlPointMixin
from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.sd.SDFragmentOperator import SDFragmentOperator
from umlshapes.sd.SDInteractionOperand import SDInteractionOperand
from umlshapes.sd.SDInteractionOperand import SDInteractionOperands

from umlshapes.utils.ResourceUtils import ResourceUtils

if TYPE_CHECKING:
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

DEFAULT_FRAGMENT_WIDTH:  int = 200
DEFAULT_FRAGMENT_HEIGHT: int = 120
BADGE_NOTCH_SIZE:        int = 5
BADGE_PADDING_X:         int = 16
BADGE_PADDING_Y:         int = 6
GUARD_OFFSET_X:          int = 8
GUARD_OFFSET_Y:          int = 4


class UmlSDCombinedFragment(ControlPointMixin, IdentifierMixin, RectangleShape, TopLeftMixin):
    """
    Represents an OMG UML 2.5.1 Combined Fragment (Section 17.6) enclosing
    interaction operands with an operator badge (alt, opt, loop, par, etc.),
    dashed operand divider lines, and guard conditions.
    """

    def __init__(
        self,
        operator: SDFragmentOperator = SDFragmentOperator.ALT,
        operands: Optional[SDInteractionOperands] = None,
        x: float = 0.0,
        y: float = 0.0,
        width:  float = DEFAULT_FRAGMENT_WIDTH,
        height: float = DEFAULT_FRAGMENT_HEIGHT
    ):
        """
        Initialize a combined fragment shape.

        Args:
            operator: The fragment interaction operator (e.g. ALT, OPT, LOOP, PAR).
            operands: Optional initial interaction operand compartments.
            x:      Initial horizontal center coordinate.
            y:      Initial vertical center coordinate.
            width:  Initial bounding box width.
            height: Initial bounding box height.
        """
        self.logger:       Logger             = getLogger(__name__)
        self._preferences: UmlPreferences     = UmlPreferences()
        self._operator:    SDFragmentOperator = operator

        initialOperands: SDInteractionOperands
        if operands is not None:
            initialOperands = operands
        else:
            initialOperands = SDInteractionOperands([])
        self._operands: SDInteractionOperands = initialOperands

        ControlPointMixin.__init__(self, shape=self)
        IdentifierMixin.__init__(self)
        RectangleShape.__init__(self, w=width, h=height)
        TopLeftMixin.__init__(self, umlShape=self, width=round(width), height=round(height))

        self.SetX(x)
        self.SetY(y)
        self.SetBrush(TRANSPARENT_BRUSH)
        self.SetPen(ResourceUtils.blackSolidPen())
        self.SetCentreResize(False)

    @property
    def operator(self) -> SDFragmentOperator:
        return self._operator

    @operator.setter
    def operator(self, operator: SDFragmentOperator):
        self._operator = operator

    @property
    def operands(self) -> SDInteractionOperands:
        return self._operands

    @operands.setter
    def operands(self, operands: SDInteractionOperands):
        self._operands = operands

    @property
    def umlFrame(self) -> 'SequenceDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'SequenceDiagramFrame'):
        self.SetCanvas(frame)
        if frame is not None:
            if hasattr(frame, 'umlPubSubEngine'):
                from umlshapes.lib.ogl import ShapeEvtHandler
                from umlshapes.sd.eventhandlers.UmlSDCombinedFragmentEventHandler import UmlSDCombinedFragmentEventHandler

                currentHandler: ShapeEvtHandler = self.GetEventHandler()
                if not isinstance(currentHandler, UmlSDCombinedFragmentEventHandler):
                    eventHandler: UmlSDCombinedFragmentEventHandler = UmlSDCombinedFragmentEventHandler(
                        umlSDCombinedFragment=self,
                        umlPubSubEngine=frame.umlPubSubEngine,
                        previousEventHandler=currentHandler
                    )
                    self.SetEventHandler(eventHandler)

    def setPosition(self, x: float, y: float):
        """
        Set horizontal and vertical center coordinates.

        Args:
            x: Center X coordinate.
            y: Center Y coordinate.
        """
        self.SetX(x)
        self.SetY(y)

    def getControlPoints(self) -> list[ControlPoint]:
        """
        Return the control points (sizing handles) for this shape.
        """
        return self._controlPoints

    def addOperand(self, guard: str = '', startTimeStep: int = 0, endTimeStep: int = 0) -> SDInteractionOperand:
        """
        Add a new interaction operand compartment to this combined fragment.

        Args:
            guard: Optional guard condition text (e.g. '[x > 0]')
            startTimeStep: Starting discrete time step index
            endTimeStep: Ending discrete time step index

        Returns:
            The newly created operand
        """
        operand: SDInteractionOperand = SDInteractionOperand(
            guard=guard,
            startTimeStep=startTimeStep,
            endTimeStep=endTimeStep
        )
        self._operands.append(operand)
        return operand

    def removeOperand(self, index: int):
        """
        Remove an interaction operand by its index.

        Args:
            index: Zero-based index of the operand to remove
        """
        if 0 <= index < len(self._operands):
            del self._operands[index]

    def HitTest(self, x: float, y: float) -> tuple[int, float] | bool:
        """
        Hit test covering the fragment boundary frame and interior regions.
        """
        halfWidth: float = self.GetWidth() / 2.0
        halfHeight: float = self.GetHeight() / 2.0

        left:   float = self.GetX() - halfWidth
        right:  float = self.GetX() + halfWidth
        top:    float = self.GetY() - halfHeight
        bottom: float = self.GetY() + halfHeight

        if (left <= x <= right) and (top <= y <= bottom):
            return 0, abs(x - self.GetX())
        return False

    def OnDraw(self, dc: MemoryDC):
        """
        Draw the combined fragment: outer frame, operator badge, dashed dividers, and guards.
        """
        halfWidth: float = self.GetWidth() / 2.0
        halfHeight: float = self.GetHeight() / 2.0

        leftX: int = round(self.GetX() - halfWidth)
        topY: int = round(self.GetY() - halfHeight)
        boxWidth: int = round(self.GetWidth())
        boxHeight: int = round(self.GetHeight())
        rightX: int = leftX + boxWidth

        isHighlighted: bool = False
        if self.AncestorSelected() is True:
            isHighlighted = True
        elif self.Selected() is True:
            isHighlighted = True

        borderPen: Pen
        dividerPen: Pen
        if isHighlighted:
            borderPen = ResourceUtils.redDashedPen()
            dividerPen = ResourceUtils.redDashedPen()
        else:
            borderPen = ResourceUtils.blackSolidPen()
            dividerPen = ResourceUtils.blackDashedPen()

        dc.SetPen(borderPen)
        dc.SetBrush(TRANSPARENT_BRUSH)
        dc.DrawRectangle(leftX, topY, boxWidth, boxHeight)

        self._drawOperatorBadge(dc=dc, leftX=leftX, topY=topY, borderPen=borderPen)
        self._drawOperands(dc=dc, leftX=leftX, topY=topY, rightX=rightX, boxHeight=boxHeight, dividerPen=dividerPen)

    def _drawOperatorBadge(self, dc: MemoryDC, leftX: int, topY: int, borderPen: Pen):
        dc.SetFont(ResourceUtils.defaultFont())
        operatorText: str = self._operator.value
        textExtent: Size = dc.GetTextExtent(operatorText)

        badgeWidth: int = max(self._preferences.fragmentHeaderWidth, textExtent.width + BADGE_PADDING_X)
        badgeHeight: int = max(self._preferences.fragmentHeaderHeight, textExtent.height + BADGE_PADDING_Y)

        badgePoints: list[Point] = [
            Point(leftX, topY),
            Point(leftX + badgeWidth, topY),
            Point(leftX + badgeWidth, topY + badgeHeight - BADGE_NOTCH_SIZE),
            Point(leftX + badgeWidth - BADGE_NOTCH_SIZE, topY + badgeHeight),
            Point(leftX, topY + badgeHeight),
        ]

        dc.SetPen(borderPen)
        dc.SetBrush(ResourceUtils.backGroundBrush())
        dc.DrawPolygon(badgePoints)

        textX: int = leftX + ((badgeWidth - BADGE_NOTCH_SIZE - textExtent.width) // 2)
        textY: int = topY + ((badgeHeight - textExtent.height) // 2)
        dc.SetTextForeground(BLACK)
        dc.DrawText(operatorText, textX, textY)

    def _drawOperands(self, dc: MemoryDC, leftX: int, topY: int, rightX: int, boxHeight: int, dividerPen: Pen):
        if len(self._operands) == 0:
            return

        operandCount: int = len(self._operands)
        operandHeight: float = boxHeight / operandCount

        dc.SetFont(ResourceUtils.defaultFont())
        dc.SetTextForeground(BLACK)

        for index, operand in enumerate(self._operands):
            currentTopY: int = topY + round(index * operandHeight)

            if index > 0:
                dc.SetPen(dividerPen)
                dc.DrawLine(leftX, currentTopY, rightX, currentTopY)

            if operand.guard != '':
                guardText: str = operand.guard.strip()
                if not guardText.startswith('['):
                    guardText = f'[{guardText}]'

                guardX: int
                guardY: int
                if index == 0:
                    badgeWidth: int = max(self._preferences.fragmentHeaderWidth, dc.GetTextExtent(self._operator.value).width + BADGE_PADDING_X)
                    guardX = leftX + badgeWidth + GUARD_OFFSET_X
                    guardY = topY + GUARD_OFFSET_Y
                else:
                    guardX = leftX + GUARD_OFFSET_X
                    guardY = currentTopY + GUARD_OFFSET_Y

                dc.DrawText(guardText, guardX, guardY)

    def __str__(self) -> str:
        return f'UmlSDCombinedFragment(id={self.id}, operator={self._operator.value}, operands={len(self._operands)})'

    def __repr__(self) -> str:
        return self.__str__()
