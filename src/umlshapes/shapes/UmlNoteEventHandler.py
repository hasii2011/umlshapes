
from logging import Logger
from logging import getLogger

from umlshapes.shapes.UmlBaseEventHandler import UmlBaseEventHandler


class UmlNoteEventHandler(UmlBaseEventHandler):

    def __init__(self):
        self.logger: Logger = getLogger(__name__)
        super().__init__()

