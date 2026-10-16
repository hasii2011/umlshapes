
from logging import Logger
from logging import getLogger

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler


class UmlSDMessageLabelEventHandler(UmlBaseEventHandler):
    """
    Event handler for Sequence Diagram Message Labels.
    """

    def __init__(self, previousEventHandler: ShapeEvtHandler):
        self.logger: Logger = getLogger(__name__)
        super().__init__(previousEventHandler=previousEventHandler)

