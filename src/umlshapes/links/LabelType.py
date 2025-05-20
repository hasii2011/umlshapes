from enum import StrEnum


class LabelType(StrEnum):

    SOURCE_CARDINALITY      = 'Source Cardinality'
    DESTINATION_CARDINALITY = 'Destination Cardinality'
    ASSOCIATION_NAME        = 'Association Name'

    NOT_SET = 'Not Set'
