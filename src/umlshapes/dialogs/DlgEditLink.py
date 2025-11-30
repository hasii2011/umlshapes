
from logging import Logger
from logging import getLogger

from wx import CANCEL
from wx import CAPTION
from wx import CLOSE_BOX
from wx import EVT_BUTTON
from wx import ID_ANY
from wx import ID_OK
from wx import ID_CANCEL
from wx import OK
from wx import RESIZE_BORDER
from wx import STAY_ON_TOP

from wx import Size
from wx import Sizer
from wx import StaticBitmap
from wx import CommandEvent
from wx import StaticText
from wx import TextCtrl

from wx.lib.embeddedimage import PyEmbeddedImage
from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

from umlmodel.Link import Link
from umlmodel.enumerations.LinkType import LinkType


class DlgEditLink (SizedDialog):
    """
    Dialog to edit links between classes

    Usage:
        with DlgEditLink(parent, link) as dlg:
            if dlg.ShowModal() == OK:
                link = dlg.value

    The input model ink is only updated on Ok;  Else if the dialog is
    "canceled" any updated values are discarded
    """
    def __init__(self, parent, link: Link):
        """
        """
        super().__init__(parent, ID_ANY, "Edit Link", style=RESIZE_BORDER | CAPTION | CLOSE_BOX | STAY_ON_TOP)

        self.logger: Logger = getLogger(__name__)

        self._modelLink: Link = link

        sizedPanel: SizedPanel = self.GetContentsPane()
        self._imgArrow: StaticBitmap = self._linkImage(sizedPanel, link.linkType)

        gridPanel: SizedPanel = SizedPanel(parent=sizedPanel)
        gridPanel.SetSizerType("grid", {"cols": 3})   # 3-column grid layout
        gridPanel.SetSizerProps(expand=True, proportion=1)

        #  labels
        StaticText(gridPanel, label="Source Cardinality").SetSizerProps(halign="left")
        StaticText(gridPanel, label="Relationship").SetSizerProps(halign="center")
        StaticText(gridPanel, label="Destination Cardinality").SetSizerProps(halign="right")
        #  text
        self._sourceCardinality:      TextCtrl = TextCtrl(gridPanel, value="", size=Size(120, -1))
        self._relationship:           TextCtrl = TextCtrl(gridPanel, value="", size=Size(120, -1))
        self._destinationCardinality: TextCtrl = TextCtrl(gridPanel, value="", size=Size(120, -1))

        self._sourceCardinality.SetSizerProps(halign="left")
        self._relationship.SetSizerProps(halign="center")
        self._destinationCardinality.SetSizerProps(halign="right")

        buttonContainer: Sizer = self.CreateStdDialogButtonSizer(OK | CANCEL)
        self.SetButtonSizer(buttonContainer)
        # btnOk.SetDefault()

        self._setValues(link.name, link.sourceCardinality, link.destinationCardinality)

        #  button events
        self.Bind(EVT_BUTTON, self._onCmdOk,     id=ID_OK)
        self.Bind(EVT_BUTTON, self._onCmdCancel, id=ID_CANCEL)

        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

    @property
    def value(self) -> Link:
        self._modelLink.name = self._relationship.GetValue()

        self._modelLink.sourceCardinality      = self._sourceCardinality.GetValue()
        self._modelLink.destinationCardinality = self._destinationCardinality.GetValue()

        return self._modelLink

    def _createDialogButtonsContainer(self, buttons=OK) -> Sizer:

        hs: Sizer = self.CreateSeparatedButtonSizer(buttons)
        return hs

    def _linkImage(self, parent: SizedPanel, linkType: LinkType) -> StaticBitmap:
        """
        Provide an example image in linkImage
        """
        from codeallyadvanced.resources.images.icons.embedded16.ImgToolboxRelationshipAssociation import embeddedImage as ImgToolboxRelationshipAssociation
        from codeallyadvanced.resources.images.icons.embedded16.ImgToolboxRelationshipAggregation import embeddedImage as ImgToolboxRelationshipAggregation
        from codeallyadvanced.resources.images.icons.embedded16.ImgToolboxRelationshipComposition import embeddedImage as ImgToolboxRelationshipComposition
        linkTypeToImage = {
            LinkType.ASSOCIATION: ImgToolboxRelationshipAssociation,
            LinkType.AGGREGATION: ImgToolboxRelationshipAggregation,
            LinkType.COMPOSITION: ImgToolboxRelationshipComposition,
        }
        embeddedImage: PyEmbeddedImage = linkTypeToImage[linkType]
        linkImage:     StaticBitmap    = StaticBitmap(parent, ID_ANY, embeddedImage.GetBitmap())

        return linkImage

    # noinspection PyUnusedLocal
    def _onCmdOk(self, event: CommandEvent):
        """
        Handle click "Ok" button

        Args:
            event:
        """
        self.SetReturnCode(OK)
        self.EndModal(OK)

    # noinspection PyUnusedLocal
    def _onCmdCancel(self, event: CommandEvent):
        """
        """
        self.SetReturnCode(CANCEL)
        self.EndModal(CANCEL)

    def _setValues(self, relationship: str, sourceCardinality: str, destinationCardinality: str):
        """

        Args:
            relationship: the relationship between the two entities
            sourceCardinality: the source cardinality
            destinationCardinality: the source cardinality
        """
        self._relationship.SetValue(relationship)

        self._sourceCardinality.SetValue(sourceCardinality)
        self._destinationCardinality.SetValue(destinationCardinality)
