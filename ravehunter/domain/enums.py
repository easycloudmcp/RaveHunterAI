from enum import Enum


class EventSource(str, Enum):
    INSTAGRAM = "instagram"
    SHOTGUN = "shotgun"
    RESIDENT_ADVISOR = "resident_advisor"
    DICE = "dice"
    EVENTBRITE = "eventbrite"
    FACEBOOK = "facebook"
    CLUB_WEBSITE = "club_website"
    MANUAL = "manual"


class EventStatus(str, Enum):
    DISCOVERED = "discovered"
    CLASSIFIED = "classified"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"