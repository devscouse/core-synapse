import functools
from enum import StrEnum, auto
from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(StrEnum):
    local = auto()
    dev = auto()
    sit = auto()
    uat = auto()
    prod = auto()


class Cfg(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    env: Env

cfg = Cfg()
