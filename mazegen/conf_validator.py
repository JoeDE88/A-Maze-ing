import sys
import random
from typing_extensions import TypedDict, NotRequired
from dotenv import dotenv_values
from .custom_exceptions import (CapitalizedError,
                                KeyValueError,
                                MissingKeyError,
                                OutBoundsError,
                                SameDoorsError,
                                SizeError,
                                WrongUsageError)


class ConfigModel(TypedDict):
    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool
    SEED: NotRequired[str | None]


keys_list: set[str] = {
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT"
}


def outbound_value(coord: tuple[int, int], width: int, height: int,
                   door: str) -> tuple[str, str]:
    if coord[0] < 0 or coord[0] >= height:
        return (door, "row")
    if coord[1] < 0 or coord[1] >= width:
        return (door, "column")
    return ("", "")


def check_inbounds(config: ConfigModel) -> None:
    door, data = outbound_value(config["ENTRY"], config["WIDTH"],
                                config["HEIGHT"], "ENTRY")
    if door:
        raise OutBoundsError(door, data)
    door, data = outbound_value(config["EXIT"], config["WIDTH"],
                                config["HEIGHT"], "EXIT")
    if door:
        raise OutBoundsError(door, data)


def check_dimensions(config: ConfigModel) -> None:
    if config["WIDTH"] <= 1 or config["HEIGHT"] <= 1:
        dimension = "WIDTH"
        if config["HEIGHT"] < config["WIDTH"]:
            dimension = "HEIGHT"
        raise SizeError(dimension)


def check_same_doors(entry: tuple[int, int],
                     exit: tuple[int, int]) -> bool:
    return entry == exit


def parse_config(config: ConfigModel) -> None:
    check_dimensions(config)
    check_inbounds(config)
    if check_same_doors(config["ENTRY"], config["EXIT"]):
        raise SameDoorsError()


def cast_value(value: str) -> tuple[int, int]:
    x, y = value.split(",")
    keys = (int(x), int(y))
    return keys


def parse_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    else:
        raise CapitalizedError("PERFECT must be True or False")


def check_keys_values(env: dict[str, str | None]) -> None:
    for key, value in env.items():
        if value is None:
            raise KeyValueError(sys.argv[1], key)


def check_config() -> ConfigModel:
    if len(sys.argv) != 2:
        raise WrongUsageError(sys.argv[0])
    env: dict[str, str | None] = {}
    for key, value in dotenv_values(sys.argv[1]).items():
        key = key.upper()
        env.update({key: value})
    diff = set(keys_list).difference(env.keys())
    if diff:
        raise MissingKeyError(sys.argv[1], list(diff))
    check_keys_values(env)
    assert isinstance(env["ENTRY"], str)
    assert isinstance(env["EXIT"], str)
    assert isinstance(env["PERFECT"], str)
    config: ConfigModel = {
        "WIDTH": int(str(env["WIDTH"])),
        "HEIGHT": int(str(env["HEIGHT"])),
        "ENTRY": cast_value(env["ENTRY"]),
        "EXIT": cast_value(env["EXIT"]),
        "OUTPUT_FILE": str(str(env["OUTPUT_FILE"])),
        "PERFECT": parse_bool(env["PERFECT"])
    }
    if "SEED" in env and env["SEED"] != "":
        random.seed(env["SEED"])
    parse_config(config)
    return config
