"""Sales domain value objects."""

from .money import Money
from .stage import Stage, StageType
from .contact_info import ContactInfo, PhoneNumber

__all__ = [
    "Money",
    "Stage",
    "StageType", 
    "ContactInfo",
    "PhoneNumber",
]