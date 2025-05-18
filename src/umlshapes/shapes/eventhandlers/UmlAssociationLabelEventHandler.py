
from typing import cast

from logging import Logger
from logging import getLogger

from umlshapes.links.DeltaXY import DeltaXY

from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.shapes.eventhandlers.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.types.Common import LeftCoordinate
from umlshapes.types.Common import NAME_IDX
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

        from umlshapes.links.UmlLink import UmlLink

        self._debugPrint(f'xy=({x},{y})')

        umlAssociationLabel: UmlAssociationLabel = cast(UmlAssociationLabel, self.GetShape())
        umlLink:             UmlLink             = umlAssociationLabel.parent

        labelPosition: UmlPosition = umlAssociationLabel.position
        linkLabelX, linkLabelY = umlLink.GetLabelPosition(NAME_IDX)

        #
        #
        leftCoordinate: LeftCoordinate = self._convertToTopLeft(x=x, y=y, umlAssociationLabel=umlAssociationLabel)
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
        self.logger.info(f'{leftCoordinate=} {deltaXY=}')
        umlAssociationLabel.nameDelta = deltaXY

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
            self.logger.info(message)
            self._currentDebugCount = REPORT_INTERVAL
        else:
            self._currentDebugCount -= 1
