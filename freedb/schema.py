from enum import Enum

class FieldType(Enum):
    """

    https://docs.mongodb.com/manual/reference/bson-types/
    """
    Double = 1
    String = 2
    Boolean = 8
    Date = 9


