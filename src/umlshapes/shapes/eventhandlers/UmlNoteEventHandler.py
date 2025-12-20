
from logging import Logger
from logging import getLogger

from wx import DC
from wx import OK

from umlmodel.Note import Note

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.shapes.UmlNote import UmlNote

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

from umlshapes.dialogs.DlgEditNote import DlgEditNote

from umlshapes.frames.UmlFrame import UmlFrame


class UmlNoteEventHandler(UmlBaseEventHandler):
    """
    Nothing special here;  Just some syntactic sugar
    """
    def __init__(self, previousEventHandler: ShapeEvtHandler):

        self.logger: Logger = getLogger(__name__)
        super().__init__(previousEventHandler=previousEventHandler)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlNote:   UmlNote = self.GetShape()
        modelNote: Note    = umlNote.modelNote

        umlFrame:  UmlFrame  = umlNote.GetCanvas()

        with DlgEditNote(parent=umlFrame, note=modelNote, ) as dlg:
            if dlg.ShowModal() == OK:
                umlFrame.refresh()

        umlNote.selected = False

    def OnMoveLink(self, dc: DC, moveControlPoints: bool = True):
        """

        Args:
            dc:
            moveControlPoints:
        """
        super().OnMoveLink(dc=dc, moveControlPoints=moveControlPoints)
