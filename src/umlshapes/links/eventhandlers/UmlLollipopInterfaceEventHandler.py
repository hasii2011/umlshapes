
from logging import Logger
from logging import getLogger

from umlshapes.eventhandlers.UmlBaseEventHandler import UmlBaseEventHandler

from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface


class UmlLollipopInterfaceEventHandler(UmlBaseEventHandler):

    def __init__(self, lollipopInterface: UmlLollipopInterface):

        self.logger: Logger = getLogger(__name__)
        super().__init__(shape=lollipopInterface)
