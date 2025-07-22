from typing import Callable

from abc import ABC
from abc import abstractmethod

from umlshapes.eventengine.UmlEventType import UmlEventType


class IUmlEventEngine(ABC):
    """
    Implement an interface using the standard Python library.  I found zope too abstract
    and python interface could not handle subclasses
    """
    @abstractmethod
    def registerListener(self, eventType: UmlEventType, callback: Callable):
        pass

    @abstractmethod
    def sendEvent(self, eventType: UmlEventType, **kwargs):
        pass
