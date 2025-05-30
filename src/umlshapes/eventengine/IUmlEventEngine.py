from typing import Callable

from abc import ABC
from abc import abstractmethod

from wx import PyEventBinder

from umlshapes.eventengine.UmlEvents import UmlEventType


class IUmlEventEngine(ABC):
    """
    Implement an interface using the standard Python library.  I found zope too abstract
    and python interface could not handle subclasses
    """
    @abstractmethod
    def registerListener(self, event: PyEventBinder, callback: Callable):
        pass

    @abstractmethod
    def sendEvent(self, eventType: UmlEventType, **kwargs):
        pass
