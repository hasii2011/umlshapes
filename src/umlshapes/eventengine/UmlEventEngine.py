
from typing import Callable

from logging import Logger
from logging import getLogger

from wx import Point
from wx import PostEvent
from wx import Window
from wx import PyEventBinder

from umlshapes.eventengine.InvalidKeywordException import InvalidKeywordException

from umlshapes.eventengine.IUmlEventEngine import IUmlEventEngine
from umlshapes.eventengine.UmlEvents import CutOglClassEvent
from umlshapes.eventengine.UmlEvents import DiagramFrameModifiedEvent
from umlshapes.eventengine.UmlEvents import RequestLollipopLocationEvent
from umlshapes.eventengine.UmlEvents import ShapeSelectedEvent
from umlshapes.eventengine.UmlEvents import UmlEventType
from umlshapes.eventengine.UmlShapeSelectedData import UmlShapeSelectedData

from umlshapes.types.Common import UmlShape

CUT_OGL_CLASS_PARAMETER:             str = 'shapeToCut'
REQUEST_LOLLIPOP_LOCATION_PARAMETER: str = 'requestShape'
SELECTED_SHAPE_PARAMETER:            str = 'selectedShape'
SELECTED_SHAPE_POSITION_PARAMETER:   str = 'selectedShapePosition'
CALLBACK_PARAMETER:                  str = 'callback'


class UmlEventEngine(IUmlEventEngine):
    """
    The rationale for this class is to isolate the underlying implementation
    of events.  Currently, it depends on the wxPython event loop.  This leaves
    it open to other implementations;

    Get one of these for each Window you want to listen on
    """
    def __init__(self, listeningWindow: Window):

        self._listeningWindow: Window = listeningWindow
        self.logger: Logger = getLogger(__name__)

    def registerListener(self, event: PyEventBinder, callback: Callable):
        self._listeningWindow.Bind(event, callback)

    def sendEvent(self, eventType: UmlEventType, **kwargs):
        """
        Args:
            eventType:
            **kwargs:
        """
        try:
            # noinspection PyUnreachableCode
            match eventType:
                case UmlEventType.DiagramFrameModified:
                    self._sendDiagramFrameModifiedEvent()
                case UmlEventType.RequestLollipopLocation:
                    self._sendRequestLollipopLocationEvent(**kwargs)
                case UmlEventType.CutOglClass:
                    self._sendCutShapeEvent(**kwargs)
                case UmlEventType.ShapeSelected:
                    self._sendSelectedShapeEvent(**kwargs)
                case _:
                    self.logger.warning(f'Unknown Ogl Event Type: {eventType}')
        except KeyError as ke:
            eMsg: str = f'Invalid keyword parameter. `{ke}`'
            raise InvalidKeywordException(eMsg)

    def _sendSelectedShapeEvent(self, **kwargs):

        from umlshapes.shapes.UmlClass import UmlClass

        shape:    UmlClass = kwargs[SELECTED_SHAPE_PARAMETER]
        position: Point    = kwargs[SELECTED_SHAPE_POSITION_PARAMETER]

        eventData:     UmlShapeSelectedData = UmlShapeSelectedData(shape=shape, position=position)
        selectedEvent: ShapeSelectedEvent     = ShapeSelectedEvent(shapeSelectedData=eventData)

        PostEvent(dest=self._listeningWindow, event=selectedEvent)

    def _sendCutShapeEvent(self, **kwargs):

        shapeToCut = kwargs[CUT_OGL_CLASS_PARAMETER]

        cutOglClassEvent: CutOglClassEvent = CutOglClassEvent(selectedShape=shapeToCut)
        PostEvent(dest=self._listeningWindow, event=cutOglClassEvent)

    def _sendDiagramFrameModifiedEvent(self):
        eventToPost: DiagramFrameModifiedEvent = DiagramFrameModifiedEvent()
        PostEvent(dest=self._listeningWindow, event=eventToPost)

    def _sendRequestLollipopLocationEvent(self, **kwargs):

        requestShape: UmlShape                     = kwargs[REQUEST_LOLLIPOP_LOCATION_PARAMETER]
        eventToPost:  RequestLollipopLocationEvent = RequestLollipopLocationEvent(requestShape=requestShape)
        PostEvent(dest=self._listeningWindow, event=eventToPost)

