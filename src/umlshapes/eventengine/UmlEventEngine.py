
from typing import Callable

from logging import Logger
from logging import getLogger

from umlshapes.eventengine.BaseEventEngine import BaseEventEngine
from umlshapes.eventengine.BaseEventEngine import Topic
from umlshapes.eventengine.IUmlEventEngine import FrameId

from umlshapes.eventengine.IUmlEventEngine import IUmlEventEngine
from umlshapes.eventengine.UmlEventType import UmlEventType


class UmlEventEngine(IUmlEventEngine, BaseEventEngine):
    """
    The rationale for this class is to isolate the underlying implementation
    of events.  Currently, it depends on the wxPython event loop.  This leaves
    it open to other implementations;

    Get one of these for each Window you want to listen on
    """
    def __init__(self):

        self.logger: Logger = getLogger(__name__)

    def registerListener(self, eventType: UmlEventType, frameId: FrameId, callback: Callable):
        self._subscribe(topic=self._toTopic(eventType, frameId), callback=callback)

    def sendEvent(self, eventType: UmlEventType, frameId: FrameId, **kwargs):
        self._sendMessage(topic=self._toTopic(eventType, frameId), **kwargs)

    def _toTopic(self, eventType: UmlEventType, frameId: FrameId) -> Topic:

        topic: Topic = Topic(f'{eventType.value}.{frameId}')
        return topic
