
from logging import Logger
from logging import getLogger

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.types.Common import ModelObject


class UmlObject:

    def __init__(self, modelObject: ModelObject = None):
        """

        Args:
            modelObject:  The data model object
        """

        self.baseLogger:   Logger         = getLogger(__name__)
        self._modelObject: ModelObject    = modelObject
        self._preferences: UmlPreferences = UmlPreferences()

    @property
    def modelObject(self) -> ModelObject:
        return self._modelObject

    @modelObject.setter
    def modelObject(self, pyutObject: ModelObject):
        self._modelObject = pyutObject
