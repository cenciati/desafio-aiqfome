from dataclasses import dataclass


def strict_record(cls):
    return dataclass(cls, slots=True, frozen=True, kw_only=True)
