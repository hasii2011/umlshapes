
from logging import Logger
from logging import getLogger

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.shapes.eventhandlers.UmlBaseEventHandler import UmlBaseEventHandler


class UmlActorEventHandler(UmlBaseEventHandler):
    """
    Nothing special here;  Just some syntactic sugar
    """

    def __init__(self):
        self.logger:       Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()
        super().__init__()
