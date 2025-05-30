
from enum import Enum

from wx.lib.newevent import NewEvent

#
# The constructor returns a tuple; The first entry is the event,  The second is the binder
#
ShapeSelectedEvent,        EVT_SHAPE_SELECTED         = NewEvent()
CutOglClassEvent,          EVT_CUT_OGL_CLASS          = NewEvent()
DiagramFrameModifiedEvent, EVT_DIAGRAM_FRAME_MODIFIED = NewEvent()

RequestLollipopLocationEvent, EVT_REQUEST_LOLLIPOP_LOCATION = NewEvent()
CreateLollipopInterfaceEvent, EVT_CREATE_LOLLIPOP_INTERFACE = NewEvent()


class UmlEventType(Enum):
    """

    """

    ShapeSelected           = 'ShapeSelected'
    CutOglClass             = 'CutOglClass'
    DiagramFrameModified    = 'DiagramFrameModified'
    RequestLollipopLocation = 'RequestLollipopLocation'
    CreateLollipopInterface = 'CreateLollipopInterface'
