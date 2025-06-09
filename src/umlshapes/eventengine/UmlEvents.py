
from enum import Enum

from wx.lib.newevent import NewEvent

#
# The constructor returns a tuple; The first entry is the event,  The second is the binder
#
ShapeSelectedEvent,        EVT_SHAPE_SELECTED         = NewEvent()
CutOglClassEvent,          EVT_CUT_OGL_CLASS          = NewEvent()
DiagramFrameModifiedEvent, EVT_DIAGRAM_FRAME_MODIFIED = NewEvent()

RequestLollipopLocationEvent, EVT_REQUEST_LOLLIPOP_LOCATION = NewEvent()


class UmlEventType(Enum):
    """

    """

    ShapeSelected           = EVT_SHAPE_SELECTED.typeId
    CutOglClass             = EVT_CUT_OGL_CLASS.typeId
    DiagramFrameModified    = EVT_DIAGRAM_FRAME_MODIFIED.typeId
    RequestLollipopLocation = EVT_REQUEST_LOLLIPOP_LOCATION.typeId
