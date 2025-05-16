
from typing import cast

from logging import Logger
from logging import getLogger

from umlshapes.links.DeltaXY import DeltaXY
from umlshapes.links.LinkCommon import getClosestPointOnLine
from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.shapes.eventhandlers.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.types.ClosestPoint import ClosestPoint
from umlshapes.types.Common import NAME_IDX

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

        super().OnMovePost(dc, x, y, oldX, oldY, display)

        from umlshapes.links.UmlLink import UmlLink

        self._debugPrint(f'xy=({x},{y})')

        umlAssociationLabel: UmlAssociationLabel = cast(UmlAssociationLabel, self.GetShape())
        umlLink:             UmlLink             = umlAssociationLabel.parent

        labelX, labelY = umlLink.GetLabelPosition(NAME_IDX)

        #
        #
        #
        deltaXY: DeltaXY = DeltaXY(
            deltaX=labelX - x,
            deltaY=labelY - y
        )
        self.logger.info(f'{deltaXY=}')
        umlAssociationLabel.nameDelta = deltaXY

    def _debugPrint(self, message: str):

        if self._currentDebugCount <= 0:
            self.logger.info(message)
