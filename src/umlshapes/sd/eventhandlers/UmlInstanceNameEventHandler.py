from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlshapes.lib.ogl import ShapeEvtHandler

if TYPE_CHECKING:
    from umlshapes.sd.UmlInstanceName import UmlInstanceName
    from umlshapes.sd.UmlSDInstance import UmlSDInstance


class UmlInstanceNameEventHandler(ShapeEvtHandler):
    """
    Event handler for the sequence diagram instance name box (header).
    Delegates click, drag, and double-click events to the parent UmlSDInstance.
    """

    def __init__(
        self,
        umlInstanceName: 'UmlInstanceName',
        umlSDInstance: 'UmlSDInstance',
        previousEventHandler: ShapeEvtHandler
    ):
        self.logger: Logger = getLogger(__name__)
        super().__init__(prev=previousEventHandler, shape=umlInstanceName)
        self._umlInstanceName: 'UmlInstanceName' = umlInstanceName
        self._umlSDInstance:   'UmlSDInstance'   = umlSDInstance

    def OnLeftClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Delegate left click to the parent UmlSDInstance so clicking the header
        box selects the instance and displays its resize control point.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        parentHandler: ShapeEvtHandler = self._umlSDInstance.GetEventHandler()
        if parentHandler is not None:
            parentHandler.OnLeftClick(x, y, keys, attachment)

    def OnBeginDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Delegate the start of a left drag to the parent UmlSDInstance.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        parentHandler: ShapeEvtHandler = self._umlSDInstance.GetEventHandler()
        if parentHandler is not None:
            parentHandler.OnBeginDragLeft(x, y, keys, attachment)

    def OnDragLeft(self, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Delegate left drag motion to the parent UmlSDInstance.

        Args:
            draw:
            x:
            y:
            keys:
            attachment:
        """
        parentHandler: ShapeEvtHandler = self._umlSDInstance.GetEventHandler()
        if parentHandler is not None:
            parentHandler.OnDragLeft(draw, x, y, keys, attachment)

    def OnEndDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Delegate the end of a left drag to the parent UmlSDInstance.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        parentHandler: ShapeEvtHandler = self._umlSDInstance.GetEventHandler()
        if parentHandler is not None:
            parentHandler.OnEndDragLeft(x, y, keys, attachment)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Delegate left double click to the parent UmlSDInstance.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        parentHandler: ShapeEvtHandler = self._umlSDInstance.GetEventHandler()
        if parentHandler is not None:
            parentHandler.OnLeftDoubleClick(x, y, keys, attachment)

    def OnRightClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Delegate right click to the parent UmlSDInstance.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        parentHandler: ShapeEvtHandler = self._umlSDInstance.GetEventHandler()
        if parentHandler is not None:
            parentHandler.OnRightClick(x, y, keys, attachment)
