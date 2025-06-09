
from typing import cast

from logging import Logger
from logging import getLogger

from umlshapes.links.DeltaXY import DeltaXY
from umlshapes.links.LabelType import LabelType

from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.shapes.PositionReporter import PositionReporter
from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

from umlshapes.types.Common import DESTINATION_CARDINALITY_IDX
from umlshapes.types.Common import LeftCoordinate
from umlshapes.types.Common import NAME_IDX
from umlshapes.types.Common import SOURCE_CARDINALITY_IDX
from umlshapes.types.UmlPosition import UmlPosition

REPORT_INTERVAL: int = 10


class UmlAssociationLabelEventHandler(UmlBaseEventHandler):
    """
    BTW, I hate local imports
    """

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        super().__init__()

        self._currentDebugCount: int = REPORT_INTERVAL

    def OnMovePost(self, dc, x: int, y: int, oldX: int, oldY: int, display: bool = True):
        """
        Positions are reported from the center of the label
        Args:
            dc:
            x:
            y:
            oldX:
            oldY:
            display:

        Returns:

        """
        super().OnMovePost(dc, x, y, oldX, oldY, display)

        umlAssociationLabel: UmlAssociationLabel = cast(UmlAssociationLabel, self.GetShape())
        umlLink:             PositionReporter    = umlAssociationLabel.parent

        self._debugPrint(f'label type: {umlAssociationLabel.labelType} xy=({x},{y})')

        if umlAssociationLabel.labelType == LabelType.ASSOCIATION_NAME:
            linkLabelX, linkLabelY = umlLink.GetLabelPosition(NAME_IDX)
        elif umlAssociationLabel.labelType == LabelType.SOURCE_CARDINALITY:
            linkLabelX, linkLabelY = umlLink.GetLabelPosition(SOURCE_CARDINALITY_IDX)
        elif umlAssociationLabel.labelType == LabelType.DESTINATION_CARDINALITY:
            linkLabelX, linkLabelY = umlLink.GetLabelPosition(DESTINATION_CARDINALITY_IDX)
        else:
            assert False, 'Developer error unknown label type'

        labelPosition: UmlPosition = umlAssociationLabel.position
        #
        #
        #
        leftCoordinate: LeftCoordinate = self._convertToTopLeft(x=x, y=y, umlAssociationLabel=umlAssociationLabel)
        deltaXY = self._calculateDelta(labelPosition, leftCoordinate, linkLabelX, linkLabelY)
        umlAssociationLabel.linkDelta = deltaXY

    def _calculateDelta(self, labelPosition: UmlPosition, leftCoordinate: LeftCoordinate, linkLabelX, linkLabelY) -> DeltaXY:
        """

        Args:
            labelPosition:
            leftCoordinate:
            linkLabelX:
            linkLabelY:

        Returns:  The new delta from the reference point
        """
        deltaX: int = linkLabelX - leftCoordinate.x
        deltaY: int = linkLabelY - leftCoordinate.y
        if linkLabelX > labelPosition.x:
            deltaX = abs(deltaX)
        else:
            pass
        if linkLabelY > labelPosition.y:
            deltaY = abs(deltaY)
        else:
            pass
        deltaXY: DeltaXY = DeltaXY(
            deltaX=deltaX,
            deltaY=deltaY
        )
        self.logger.debug(f'{leftCoordinate=} {deltaXY=}')
        return deltaXY

    def _convertToTopLeft(self, x: int, y: int, umlAssociationLabel: UmlAssociationLabel) -> LeftCoordinate:
        """

        Args:
            x: The reported X (center)
            y: The reported Y (center)
            umlAssociationLabel:

        Returns: A left coordinate
        """

        width:  int = umlAssociationLabel.size.width
        height: int = umlAssociationLabel.size.height

        left: int = x - (width // 2)
        top:  int = y - (height // 2)

        return LeftCoordinate(x=left, y=top)

    def _debugPrint(self, message: str):

        if self._currentDebugCount <= 0:
            self.logger.debug(message)
            self._currentDebugCount = REPORT_INTERVAL
        else:
            self._currentDebugCount -= 1
