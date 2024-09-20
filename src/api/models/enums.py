from enum import Enum


class Platform(str, Enum):
    RETAIL = "retail"
    STOCKX = "stockx"
    GOAT = "goat"
    STADIUM_GOODS = "stadium_goods"
    FLIGHT_CLUB = "flight_club"


class Audience(str, Enum):
    UNISEX = "Unisex"
    MEN = "Men"
    WOMEN = "Women"
    YOUTH = "Youth"
    TODDLER = "Toddler"
    UNKNOWN = "Unknown"


class SizeStandard(str, Enum):
    MENS_US = "mens_US"
    WOMENS_US = "womens_US"
