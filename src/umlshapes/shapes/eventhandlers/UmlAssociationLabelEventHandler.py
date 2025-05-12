
from typing import cast

from logging import Logger
from logging import getLogger

from umlshapes.links.DeltaXY import DeltaXY
from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.shapes.eventhandlers.UmlBaseEventHandler import UmlBaseEventHandler


class UmlAssociationLabelEventHandler(UmlBaseEventHandler):
    """
    BTW, I hate local imports
    """

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        super().__init__()

    def OnMovePost(self, dc, x: int, y: int, oldX: int, oldY: int, display: bool = True):

        super().OnMovePost(dc, x, y, oldX, oldY, display)

        from umlshapes.links.UmlLinkEventHandler import NAME_IDX
        from umlshapes.links.UmlLink import UmlLink

        self.logger.info(f'xy=({x},{y})')

        umlAssociationLabel: UmlAssociationLabel = cast(UmlAssociationLabel, self.GetShape())
        umlLink:             UmlLink             = umlAssociationLabel.parent

        # Update the delta
        nameX, nameY       = umlLink.GetLabelPosition(NAME_IDX)
        self.logger.info(f'nameXY={(nameX, nameY)}')
        deltaXY: DeltaXY = DeltaXY(
            deltaX=nameX - x,
            deltaY=nameY -y
        )
        self.logger.info(f'{deltaXY=}')
        umlAssociationLabel.nameDelta = deltaXY
