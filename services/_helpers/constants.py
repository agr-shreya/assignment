from enum import Enum


class ServiceType(Enum):
    EMAIL = "Email"
    MESSAGE = "Message"


class ServiceStatus(Enum):
    DELIVERED = "Delivered"
    FAILED = "Failed"


class ScheduleFrequency(Enum):
    ONCE = "Once"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"
