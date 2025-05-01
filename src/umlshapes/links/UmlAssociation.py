
from typing import cast

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutLink import PyutLink

from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.links.UmlLink import UmlLink


class UmlAssociation(UmlLink):

    def __init__(self, pyutLink: PyutLink):

        super().__init__(pyutLink=pyutLink)

        self.associationLogger: Logger = getLogger(__name__)
