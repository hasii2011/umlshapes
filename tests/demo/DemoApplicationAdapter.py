
from logging import Logger
from logging import getLogger

from wx.lib.sized_controls import SizedFrame


from umlshapes.IApplicationAdapter import IApplicationAdapter


class DemoApplicationAdapter(IApplicationAdapter):
    """
    The services provided by the application
    """
    def __init__(self, frame: SizedFrame):
        self.logger: Logger = getLogger(__name__)

        self._frame: SizedFrame = frame

        super().__init__()

    def updateApplicationStatus(self, message: str):
        self._frame.SetStatusText(text=message)

    def indicateDiagramModified(self):

        self.logger.info('Diagram modified')