from enum import Enum


class Environment(str, Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    STAGING = "staging"
