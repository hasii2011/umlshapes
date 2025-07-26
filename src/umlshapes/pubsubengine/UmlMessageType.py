
from enum import Enum


class UmlMessageType(Enum):
    """

    """
    UML_SHAPE_SELECTED = 'Uml Shape Selected'
    CUT_UML_CLASS      = 'Cut Uml Class'
    DIAGRAM_MODIFIED   = 'Diagram Modified'
    CREATE_LOLLIPOP    = 'Create Lollipop'

    REQUEST_LOLLIPOP_LOCATION = 'Request Lollipop Location'
    UPDATE_APPLICATION_STATUS = 'Update Application Status'
