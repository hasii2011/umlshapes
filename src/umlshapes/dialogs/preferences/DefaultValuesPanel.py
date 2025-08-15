
from typing import List

from wx import BK_DEFAULT
from wx import ID_ANY

from wx import Bitmap
from wx import ImageList
from wx import Toolbook
from wx import Window

from wx.lib.embeddedimage import PyEmbeddedImage

from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.resources.images.DefaultPreferences import embeddedImage as DefaultPreferences

from codeallyadvanced.resources.images.icons.embedded16.ImgToolboxNote import embeddedImage as ImgToolboxNote
from codeallyadvanced.resources.images.icons.embedded16.ImgToolboxText import embeddedImage as ImgToolboxText
from codeallyadvanced.resources.images.icons.embedded16.ImgToolboxClass import embeddedImage as ImgToolboxClass
from codeallyadvanced.resources.images.icons.embedded16.ImgToolboxSequenceDiagramInstance import embeddedImage as ImgToolboxSequenceDiagramInstance
from codeallyadvanced.resources.images.icons.embedded16.ImgToolboxRelationshipComposition import embeddedImage as ImgToolboxRelationshipComposition
from codeallyadvanced.resources.images.icons.embedded16.UmlLollipop import embeddedImage as UmlLollipop

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel
from umlshapes.dialogs.preferences.valuepanels.AssociationPreferencesPanel import AssociationPreferencesPanel
from umlshapes.dialogs.preferences.valuepanels.ClassPreferencesPanel import ClassPreferencesPanel
from umlshapes.dialogs.preferences.valuepanels.DefaultNamesPanel import DefaultNamesPanel
from umlshapes.dialogs.preferences.valuepanels.LollipopPreferencesPanel import LollipopPreferencesPanel
from umlshapes.dialogs.preferences.valuepanels.NotePreferencesPanel import NotePreferencesPanel
from umlshapes.dialogs.preferences.valuepanels.SDPreferencesPanel import SDPreferencesPanel
from umlshapes.dialogs.preferences.valuepanels.TextPreferencesPanel import TextPreferencesPanel


def getNextImageID(count):
    imID = 0
    while True:
        yield imID
        imID += 1
        if imID == count:
            imID = 0


class DefaultValuesPanel(BasePreferencesPanel):

    def __init__(self, parent: Window):
        super().__init__(parent)
        self._layoutWindow(self)
        self._fixPanelSize(self)

    @property
    def name(self) -> str:
        return 'UML Configuration'

    def _layoutWindow(self, parent: SizedPanel):

        toolBook: Toolbook = Toolbook(parent, ID_ANY, style=BK_DEFAULT)
        toolBook.SetSizerProps(expand=True, proportion=1)
        #
        # Brittle code; these MUST be in the specific order
        # and the toolBook.AddPage must be in exactly that ordr
        embeddedImages: List[PyEmbeddedImage] = [ImgToolboxNote, ImgToolboxText, ImgToolboxClass, DefaultPreferences,
                                                 ImgToolboxSequenceDiagramInstance,
                                                 ImgToolboxRelationshipComposition,
                                                 UmlLollipop,
                                                 ]
        imageList:      ImageList             = ImageList(width=16, height=16)

        for embeddedImage in embeddedImages:
            bmp: Bitmap = embeddedImage.GetBitmap()
            imageList.Add(bmp)

        toolBook.AssignImageList(imageList)

        imageIdGenerator = getNextImageID(imageList.GetImageCount())

        notePreferencesPanel:  NotePreferencesPanel  = NotePreferencesPanel(parent=toolBook)
        textPreferencesPanel:  TextPreferencesPanel  = TextPreferencesPanel(parent=toolBook)
        classPreferencesPanel: ClassPreferencesPanel = ClassPreferencesPanel(parent=toolBook)
        defaultNamesPanel:     DefaultNamesPanel         = DefaultNamesPanel(parent=toolBook)
        sdPanel:               SDPreferencesPanel = SDPreferencesPanel(parent=toolBook)
        associationPreferencesPanel:  AssociationPreferencesPanel = AssociationPreferencesPanel(parent=toolBook)
        lollipopPreferencesPanel:    LollipopPreferencesPanel = LollipopPreferencesPanel(parent=toolBook)

        toolBook.AddPage(notePreferencesPanel,  text='Notes', select=False, imageId=next(imageIdGenerator))
        toolBook.AddPage(textPreferencesPanel,  text='Text',  select=False, imageId=next(imageIdGenerator))
        toolBook.AddPage(classPreferencesPanel, text='Class', select=False, imageId=next(imageIdGenerator))
        toolBook.AddPage(defaultNamesPanel,     text='Names', select=False, imageId=next(imageIdGenerator))
        toolBook.AddPage(sdPanel,               text='SD',    select=False, imageId=next(imageIdGenerator))

        toolBook.AddPage(associationPreferencesPanel,  text='Association', select=False, imageId=next(imageIdGenerator))
        toolBook.AddPage(lollipopPreferencesPanel,     text='Lollipop',    select=True,  imageId=next(imageIdGenerator))

    def _setControlValues(self):
        pass
