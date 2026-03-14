from enum import StrEnum


class LabelType(StrEnum):

    SOURCE_CARDINALITY      = 'Source Cardinality'
    DESTINATION_CARDINALITY = 'Destination Cardinality'
    ASSOCIATION_NAME        = 'Association Name'
    SD_MESSAGE_NAME         = 'SD Message Name'

    NOT_SET = 'Not Set'

    def __repr__(self) -> str:
        return f'LabelType: {self}'
