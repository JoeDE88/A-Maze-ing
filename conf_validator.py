import sys
import random
from typing_extensions import TypedDict, NotRequired
from dotenv import dotenv_values
from collections import OrderedDict


class ConfigModel(TypedDict):
    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool
    SEED: NotRequired[str | None]


default_config: ConfigModel = {
    "WIDTH": 10,
    "HEIGHT": 10,
    "ENTRY": (0,0),
    "EXIT": (0,0),
    "OUTPUT_FILE": "default_output_maze.txt",
    "PERFECT": True
}



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
    if config["WIDTH"] <= 1:
        raise Exception("Width can't be 1 or less than 1")
    elif config["HEIGHT"] <= 1:
        raise Exception("Height can't be 1 or less than 1")
    elif config["ENTRY"][0] < 0 or config["ENTRY"][1] < 0:
        raise Exception("Entry position can't be negative")
    elif config["EXIT"][0] < 0 or config["EXIT"][1] < 0:
        raise Exception("Exit position can't be negative")


def cast_value(value: str) -> tuple[int, int]:
    if value is not None:
        x, y = value.split(",")
    keys = (int(x), int(y))
    return keys


def parse_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    else:
        raise Exception("PERFECT must be True or False")


def check_values(env: dict[str, str | None]) -> None:
    for key, value in env.items():
        if value == None:
            raise Exception("Configuration file must contain 'KEY=VALUE' lines")


def check_config() -> ConfigModel:
    if len(sys.argv) != 2:
        raise Exception("Number of arguments has to be 2.\n"
                        f"Example of usage: ./{sys.argv[0]} config.txt")
    try:
        env = dotenv_values(sys.argv[1])
        diff = set(keys_list).difference(env.keys())
        if diff:
            raise Exception(f"{sys.argv[1]} file has missing keys: {list(diff)}")
        check_values(env)
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
        check_inbounds(config)
        return config
    except PermissionError as p:
        if p.errno == 13:
            print(f"Error: cant' access {sys.argv[1]}")
    except Exception as e:
        print(f"ERROR ON YOUR {sys.argv[1]} FILE:")
        print(f" {e}")
        print(f"\033[91m Creating a maze with default configuration\033[00m")
    return default_config

if __name__ == "__main__":
    env = dotenv_values(sys.argv[1])
    print(env)