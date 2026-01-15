
from typing import List
from typing import cast
from typing import NewType
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from umlmodel.SDMessage import SDMessage

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.shapes.sd.UmlSDInstance import UmlSDInstance

@dataclass
class InstanceDetails:
    attachmentPosition: UmlPosition
    sdInstance:         'UmlSDInstance'

class UmlSDMessage:
    def __init__(self, sdMessage: SDMessage):

        self.logger: Logger = getLogger(__name__)

        self._sdMessage: SDMessage = sdMessage

        self._sourceInstance:      InstanceDetails = cast(InstanceDetails, None)
        self._destinationInstance: InstanceDetails = cast(InstanceDetails, None)

    @property
    def sourceInstance(self) -> InstanceDetails:
        return self._sourceInstance

    @sourceInstance.setter
    def sourceInstance(self, attachment: InstanceDetails):
        self._sourceInstance = attachment

    @property
    def destinationInstance(self) -> InstanceDetails:
        return self._destinationInstance

    @destinationInstance.setter
    def destinationInstance(self, attachment: InstanceDetails):
        self._destinationInstance = attachment


UmlSDMessages = NewType('UmlSDMessages', List[UmlSDMessage])
