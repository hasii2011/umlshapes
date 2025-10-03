
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import MemoryDC

from pyutmodelv2.PyutLink import PyutLink

from umlshapes.lib.ogl import LineShape

from umlshapes.UmlUtils import UmlUtils

from umlshapes.links.UmlLink import UmlLink

from umlshapes.shapes.UmlClass import UmlClass

if TYPE_CHECKING:
    from umlshapes.shapes.UmlNote import UmlNote


class UmlNoteLink(UmlLink):
    """
    A note link, with dashed line and no arrows.
    Developers should NOT use the UmlLink sourceShape or destination shape properties
    """
    def __init__(self, pyutLink: PyutLink):

        super().__init__(pyutLink=pyutLink)

        self.logger: Logger = getLogger(__name__)

    @property
    def sourceNote(self) -> 'UmlNote':
        return cast('UmlNote', self.sourceShape)

    @sourceNote.setter
    def sourceNote(self, umlNote: 'UmlNote'):
        from umlshapes.shapes.UmlNote import UmlNote

        assert isinstance(umlNote, UmlNote), 'Developer error this should be a UML Note instance'
        self.sourceShape = umlNote

    @property
    def destinationClass(self) -> UmlClass:
        return cast(UmlClass, self.destinationShape)

    @destinationClass.setter
    def destinationClass(self, umlClass: UmlClass):
        assert isinstance(umlClass, UmlClass), 'Developer error this should be a UML Class instance'
        self.destinationShape = umlClass

    def OnDraw(self, dc: MemoryDC):

        assert dc is not None, 'Where is my DC'

        if self.Selected() is True:
            self.SetPen(UmlUtils.redDashedPen())
        else:
            self.SetPen(UmlUtils.blackDashedPen())
        # Hack:
        #       I want to skip the UmlLink OnDraw so this line will be drawn
        LineShape.OnDraw(self=self, dc=dc)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:

        sourceNote:       UmlNote  = self.sourceNote
        destinationClass: UmlClass = self.destinationClass

        noteId:  str = sourceNote.id
        classId: str = destinationClass.id

        return f'UmlNoteLink - from: id: {noteId} {sourceNote}  to: id: {classId} {destinationClass}'
