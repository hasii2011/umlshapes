
from logging import Logger
from logging import getLogger

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.sd.UmlSDInstance import UmlSDInstance


class UmlSdInstanceEventHandler(UmlBaseEventHandler):

    def __init__(self, umlPubSubEngine: IUmlPubSubEngine, previousEventHandler: ShapeEvtHandler, umlSDInstance: UmlSDInstance):

        self.logger: Logger = getLogger(__name__)

        super().__init__(previousEventHandler=previousEventHandler, shape=umlSDInstance)
        self._umlPubSubEngine = umlPubSubEngine
