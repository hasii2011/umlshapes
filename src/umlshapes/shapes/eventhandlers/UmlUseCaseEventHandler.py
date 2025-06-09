
from logging import Logger
from logging import getLogger

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler


class UmlUseCaseEventHandler(UmlBaseEventHandler):
    """
    Nothing special here;  Just some syntactic sugar
    """

    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        super().__init__()
