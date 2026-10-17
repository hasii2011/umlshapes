from enum import Enum


class SDMessageType(Enum):
    SYNCHRONOUS  = 'Synchronous Message'
    ASYNCHRONOUS = 'Asynchronous Message'
    RETURN       = 'Return Message'
