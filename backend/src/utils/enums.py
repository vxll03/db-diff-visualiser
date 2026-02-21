from enum import Enum as PyEnum


class RabbitTaskStatus(PyEnum):
    ACCEPTED = "Accepted"
    DONE = "Done"
    FAILED = "Failed"
