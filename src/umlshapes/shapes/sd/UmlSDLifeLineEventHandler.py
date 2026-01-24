
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import ClientDC

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.shapes.sd.UmlSDLifeLine import UmlSDLifeLine
from umlshapes.types.UmlPosition import UmlPosition


@dataclass
class LifeLineClickDetails:
    clickPosition: UmlPosition
    lifeLine:      UmlSDLifeLine


class UmlSDLifeLineEventHandler(ShapeEvtHandler):

    def __init__(self, umlSDLifeLine: UmlSDLifeLine, previousEventHandler: ShapeEvtHandler):

        self.logger: Logger = getLogger(__name__)

        super().__init__(prev=previousEventHandler, shape=umlSDLifeLine)

        self._umlSDLifeLine:   UmlSDLifeLine    = umlSDLifeLine
        self._umlPubSubEngine: IUmlPubSubEngine = cast(IUmlPubSubEngine, None)

    def _setUmlPubSubEngine(self, umlPubSubEngine: IUmlPubSubEngine):
        self._umlPubSubEngine = umlPubSubEngine

    # noinspection PyTypeChecker
    umlPubSubEngine = property(fget=None, fset=_setUmlPubSubEngine)

    def OnLeftClick(self, x: int, y: int, keys: int, attachment: int):
        """

        Args:
            x:
            y:
            keys:
            attachment:
        """

        self.logger.info(f'xy: ({x},{y})')

        sdLifeLine: UmlSDLifeLine = self.GetShape()

        umlFrame:  UmlFrame  = sdLifeLine.GetCanvas()

        self._umlPubSubEngine.sendMessage(
            messageType=UmlMessageType.SD_LIFE_LINE_CLICKED,
            frameId=umlFrame.id,
            clickDetails=LifeLineClickDetails(
                clickPosition=UmlPosition(x=x, y=y),
                lifeLine=sdLifeLine
            )
        )

    def OnDraw(self, dc: ClientDC):

        umlSDLifeLine: UmlSDLifeLine = self.GetShape()
        self.logger.debug(f'{umlSDLifeLine.umlInstanceName=} {umlSDLifeLine.instanceConstrainer=}')

        umlSDLifeLine.setLifeLineEnds()
        super().OnDraw(dc=dc)
