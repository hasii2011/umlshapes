from enum import Enum


class SDMessageType(Enum):
    SYNCHRONOUS  = 'Synchronous Message'
    ASYNCHRONOUS = 'Asynchronous Message'
    RETURN       = 'Return Message'
    LOST         = 'Lost Message'
    FOUND        = 'Found Message'
