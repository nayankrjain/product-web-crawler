from enum import IntEnum


class Status(IntEnum):
    QUEUED  = 1
    FETCHED = 2
    PARSED = 3
    FAILED = 4