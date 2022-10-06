from enum import Enum


class ServiceType(Enum):
    EMAIL = "Email"
    MESSAGE = "Message"


class ServiceStatus(Enum):
    DELIVERED = "Delivered"
    PENDING = "Pending"
    FAILED = "Failed"


class ScheduleFreq(Enum):
    ONCE = "Once"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"
