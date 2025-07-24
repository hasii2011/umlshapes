from typing import Callable

from abc import ABC
from abc import abstractmethod

from umlshapes.frames.DiagramFrame import FrameId

from umlshapes.eventengine.UmlEventType import UmlEventType


class IUmlEventEngine(ABC):
    """
    Implement an interface using the standard Python library.  I found zope too abstract
    and python interface could not handle subclasses;
    We will register a topic on a eventType.frameId.DiagramName
    """
    @abstractmethod
    def registerListener(self, eventType: UmlEventType, frameId: FrameId, callback: Callable):
        pass

    @abstractmethod
    def sendEvent(self, eventType: UmlEventType, frameId: FrameId, **kwargs):
        pass
