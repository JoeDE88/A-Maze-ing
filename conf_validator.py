import sys
import random
from typing import TypedDict, NotRequired
from dotenv import dotenv_values


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


def check_inbounds(config: ConfigModel) -> None:
    err: str | None = ""
    if config["ENTRY"][0] >= config["WIDTH"] or \
       config["ENTRY"][1] >= config["HEIGHT"]:
        err = "ENTRY"
    if config["EXIT"][0] >= config["WIDTH"] or \
       config["EXIT"][1] >= config["HEIGHT"]:
        err = "EXIT"
    if config["ENTRY"] == config["EXIT"]:
        err = "Same"
    if err == "ENTRY" or err == "EXIT":
        raise Exception(f"Coordinates out of bounds: {err}")
    if err == "Same":
        raise Exception("ENTRY and EXIT must be different")


def parse_config(config: ConfigModel) -> None:
    if config["HEIGHT"] <= 1:
        raise Exception("Width can't be 1 or less than 1")
    elif config["HEIGHT"] <= 1:
        raise Exception("Height can't be 1 or less than 1")
    elif config["ENTRY"][0] < 0 or config["ENTRY"][1] < 0:
        raise Exception("Entry position can't be negative")
    elif config["EXIT"][0] < 0 or config["EXIT"][1] < 0:
        raise Exception("Exit position can't be negative")


def cast_value(value: str | None) -> tuple[int, int]:
    if value is not None:
        x, y = value.split(",")
    keys = (int(x), int(y))
    return keys


def parse_bool(value: str | None) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    else:
        raise Exception("PERFECT must be True or False")


def check_config() -> ConfigModel:
    if len(sys.argv) != 2:
        raise Exception("Number of arguments has to be 2.\n"
                        f"Example of usage: ./{sys.argv[0]} config.txt")
    env = dotenv_values(sys.argv[1])
    if not set(keys_list).issubset(env.keys()):
        raise Exception(f"{sys.argv[1]} file has missing or invalid keys")
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
    check_inbounds(config)
    return config
