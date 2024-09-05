import time
import json

from dotenv import dotenv_values

from tinkoff.invest.schemas import Quotation

def get_current_ts():
    return time.time()

def quotation_to_float(quotation: Quotation):
    return quotation.units + quotation.nano / 10**9

def get_config(path="./config.json"):
    config = None
    with open(path, "r") as f:
        config = json.load(f)
    config["instruments"] = []
    config["figi_to_ticker"] = {}
    for k, v in config["ticker_to_figi"].items():
        config["figi_to_ticker"][v] = k
        config["instruments"].append(k)

    env_vars = dotenv_values()
    config["token"] = env_vars.get("TOKEN")

    base_treemap = get_base_treemap()
    config["base_treemap"] = base_treemap
    return config

def get_base_treemap(path="./base_treemap.json"):
    treemap = None
    with open(path, "r") as f:
        treemap = json.load(f)
    return treemap
