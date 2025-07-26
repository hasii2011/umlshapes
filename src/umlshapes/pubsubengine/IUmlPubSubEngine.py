from typing import Callable

from abc import ABC
from abc import abstractmethod

from umlshapes.frames.DiagramFrame import FrameId

from umlshapes.pubsubengine.UmlMessageType import UmlMessageType


class IUmlPubSubEngine(ABC):
    """
    Implement an interface using the standard Python library.  I found zope too abstract
    and python interface could not handle subclasses;
    We will register a topic on a eventType.frameId.DiagramName
    """
    @abstractmethod
    def subscribe(self, messageType: UmlMessageType, frameId: FrameId, callback: Callable):
        pass

    @abstractmethod
    def sendMessage(self, messageType: UmlMessageType, frameId: FrameId, **kwargs):
        pass
