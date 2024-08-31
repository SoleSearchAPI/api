from enum import Enum


class Platform(str, Enum):
    RETAIL = "retail"
    STOCKX = "stockx"
    GOAT = "goat"
    STADIUM_GOODS = "stadium_goods"


class Audience(str, Enum):
    UNISEX = "Unisex"
    MEN = "Men"
    WOMEN = "Women"
    YOUTH = "Youth"
    TODDLER = "Toddler"
    UNKNOWN = "Unknown"
