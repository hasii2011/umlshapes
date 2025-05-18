
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import ClientDC
from wx import DC

from wx.lib.ogl import ShapeCanvas
from wx.lib.ogl import ShapeEvtHandler

from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.types.Common import NAME_IDX
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.links.UmlLink import UmlLink


class UmlLinkEventHandler(ShapeEvtHandler):
    """
    BTW, I hate local imports
    """

    def __init__(self, umlLink: 'UmlLink'):

        self.logger: Logger = getLogger(__name__)

        super().__init__(shape=umlLink)

    def OnLeftClick(self, x: int, y: int, keys=0, attachment=0):
        super().OnLeftClick(x, y, keys, attachment)

        # self.logger.info(f'({x},{y}), {keys=} {attachment=}')

        umlLink: 'UmlLink' = self.GetShape()

        canvas: ShapeCanvas = umlLink.GetCanvas()
        dc:     ClientDC    = ClientDC(canvas)

        canvas.PrepareDC(dc)
        umlLink.Select(select=True, dc=dc)
        #
        # middle = umlLink.GetLabelPosition(0)
        # start  = umlLink.GetLabelPosition(1)
        # end    = umlLink.GetLabelPosition(2)
        #
        # self.logger.info(f'{middle=} {start=} {end=}')

        # controlPoints = umlLink.GetLineControlPoints()
        # self.logger.info(f'{controlPoints=}')

    def OnMoveLink(self, dc: DC, moveControlPoints: bool = True):

        super().OnMoveLink(dc=dc, moveControlPoints=moveControlPoints)

        umlLink: UmlLink = self.GetShape()
        associationName = umlLink.associationName
        #
        if associationName is not None:
            nameLabel:       UmlAssociationLabel = associationName

            labelX, labelY = umlLink.GetLabelPosition(NAME_IDX)

            newNamePosition: UmlPosition = UmlPosition(
                x=labelX - nameLabel.nameDelta.deltaX,
                y=labelY - nameLabel.nameDelta.deltaY
            )
            # self.logger.info(f'{nameLabel.closestPoint=} {newNamePosition=}')
            self.logger.info(f'deltaX,deltaY=({nameLabel.nameDelta.deltaX},{nameLabel.nameDelta.deltaY})')
            nameLabel.position = newNamePosition
            self.GetShape().GetCanvas().refresh()
            # noinspection SpellCheckingInspection
            """         
            srcCardX, srcCardY = umlLink.GetLabelPosition(SOURCE_CARDINALITY_IDX)
            dstCardX, dstCardY = umlLink.GetLabelPosition(DESTINATION_CARDINALITY_IDX)

            self.logger.info(f'src: ({srcCardX},{srcCardY}) name: ({nameX},{nameY}) dst: ({dstCardX},{dstCardY})')

            namePosition: UmlPosition = umlLink.associationName.position
            nameDelta: DeltaXY = DeltaXY(
                deltaX=namePosition.x - nameX,
                deltaY=namePosition.y - nameX
            )
            umlLink._nameDelta = nameDelta
            self.logger.info(f'{nameDelta=} before: {umlLink.associationName.position}')

            newPosition: UmlPosition = UmlPosition(
                x=namePosition.x + nameDelta.deltaX,
                y=namePosition.y + nameDelta.deltaX
            )

            umlLink.associationName.position = newPosition

            self.logger.info(f'after: {umlLink.associationName.position}')
        """
