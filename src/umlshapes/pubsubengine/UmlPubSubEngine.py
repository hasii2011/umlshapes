
from typing import Callable

from logging import Logger
from logging import getLogger

from codeallybasic.BasePubSubEngine import BasePubSubEngine
from codeallybasic.BasePubSubEngine import Topic

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.frames.DiagramFrame import FrameId


class UmlPubSubEngine(IUmlPubSubEngine, BasePubSubEngine):
    """
    The rationale for this class is to isolate the underlying implementation
    of events.  Currently, it depends on the wxPython event loop.  This leaves
    it open to other implementations;

    Get one of these for each Window you want to listen on
    """
    def __init__(self):

        self.logger: Logger = getLogger(__name__)

    def subscribe(self, messageType: UmlMessageType, frameId: FrameId, callback: Callable):
        self._subscribe(topic=self._toTopic(messageType, frameId), callback=callback)

    def sendMessage(self, messageType: UmlMessageType, frameId: FrameId, **kwargs):
        self._sendMessage(topic=self._toTopic(messageType, frameId), **kwargs)

    def _toTopic(self, eventType: UmlMessageType, frameId: FrameId) -> Topic:

        topic: Topic = Topic(f'{eventType.value}.{frameId}')
        return topic
