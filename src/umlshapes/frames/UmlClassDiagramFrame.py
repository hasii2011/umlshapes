
from logging import Logger
from logging import getLogger
from typing import cast

from wx import Window

from umlshapes.frames.UmlClassDiagramFrameMenuHandler import UmlClassDiagramFrameMenuHandler
from umlshapes.frames.UmlFrame import UmlFrame


class UmlClassDiagramFrame(UmlFrame):

    def __init__(self, parent: Window):

        super().__init__(parent=parent)

        self.ucdLogger: Logger = getLogger(__name__)

        self._menuHandler:  UmlClassDiagramFrameMenuHandler = cast(UmlClassDiagramFrameMenuHandler, None)

    def OnRightClick(self, x: int, y: int, keys: int = 0):
        self.ucdLogger.info('Ouch, you right-clicked me !!')

        if self._areWeOverAShape(x=x, y=y) is False:
            self.ucdLogger.info('You missed the shape')
            if self._menuHandler is None:
                self._menuHandler = UmlClassDiagramFrameMenuHandler(self)

            self._menuHandler.popupMenu(x=x, y=y)

    def _areWeOverAShape(self, x: int, y: int) -> bool:
        answer:         bool  = True
        shape, n = self.FindShape(x=x, y=y)
        # Don't popup over a shape
        if shape is None:
            answer = False

        return answer
