
from typing import Union

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutText import PyutText

ModelObject = Union[PyutText, None]


class UmlObject:

    def __init__(self, modelObject: ModelObject = None):
        """

        Args:
            modelObject:  The data model object
        """

        self.logger: Logger = getLogger(__name__)

        self._modelObject: ModelObject = modelObject

    @property
    def modelObject(self) -> ModelObject:
        return self._modelObject

    @modelObject.setter
    def modelObject(self, pyutObject: ModelObject):
        self._modelObject = pyutObject
