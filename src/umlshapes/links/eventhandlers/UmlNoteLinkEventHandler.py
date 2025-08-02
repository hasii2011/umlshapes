
from logging import Logger
from logging import getLogger

from umlshapes.links.UmlNoteLink import UmlNoteLink
from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler


class UmlNoteLinkEventHandler(UmlLinkEventHandler):

    def __init__(self, umlNoteLink: UmlNoteLink):
        self.logger: Logger = getLogger(__name__)

        super().__init__(umlNoteLink)
