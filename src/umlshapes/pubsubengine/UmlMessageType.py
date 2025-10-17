
from enum import Enum


class UmlMessageType(Enum):
    """

    """
    UML_SHAPE_SELECTED = 'Uml Shape Selected'
    CUT_UML_CLASS      = 'Cut Uml Class'        # Issued from UmlClassCtxMenuHandler
    FRAME_LEFT_CLICK   = 'Frame Left Click'
    FRAME_MODIFIED     = 'Frame Modified'
    SHAPE_MOVING       = 'Shape Moving'         # Only the 'master' shape issues this message


    CREATE_LOLLIPOP           = 'Create Lollipop'
    REQUEST_LOLLIPOP_LOCATION = 'Request Lollipop Location'
    UPDATE_APPLICATION_STATUS = 'Update Application Status'

    UNDO = 'Undo'
    REDO = 'Redo'

    CUT_SHAPES        = 'CutShapes'
    COPY_SHAPES       = 'CopyShapes'
    PASTE_SHAPES      = 'PasteShapes'
    SELECT_ALL_SHAPES = 'SelectAllShapes'
