import copy
import ujson
import os


from collections import defaultdict
from typing import Dict

from .rollling_window_container import (
    DefaultRollingWindowContainerWithTimestams as DefaultRollingContainer
)
from .utils import get_current_ts
from .events import TradeEvent

class TreemapDataHandler:

    def __init__(self, config) -> None:
        self._config = config
        self._containers : Dict[int, Dict[str, DefaultRollingContainer]] = dict()
        self._intervals = self._config["treemap_intervals"]
        self._last_treemaps_update_ts = get_current_ts()
        self._upadte_period = config["treemap_update_period"]
        self._base_treemap = config["base_treemap"]
        self._treemaps_cache_dir = config["treemaps_cache_dir"]
        self._treemaps : Dict[int, Dict] = dict()
        for interval in self._intervals:
            self._treemaps[interval] = self._base_treemap
            self._containers[interval] = dict()
            for i in config["instruments"]:
                self._containers[interval][i] = DefaultRollingContainer(interval)

    def _save_treemaps(self):
        for interval, treemap in self._treemaps.items():
            treemap_filename = os.path.join(self._treemaps_cache_dir, f"{interval}_treemap.json")
            with open(treemap_filename, "w") as f:
                ujson.dump(treemap, f, indent=2)

    def _get_price_deltas(self):
        price_deltas : Dict[int, Dict[str, float]] = defaultdict(lambda: defaultdict(lambda: 0))
        for interval in self._intervals:
            for instrument, cont in self._containers[interval].items():
                if cont.size() > 0:
                    price_delta = (cont.get_last().value - cont.get_first().value) / cont.get_first().value * 100
                    price_delta = round(price_delta, 2)
                    price_deltas[interval][instrument] = price_delta
        return price_deltas

    def _update_treemaps(self):
        cur_ts = get_current_ts()
        if cur_ts - self._upadte_period <= self._last_treemaps_update_ts:
            return
        self._last_treemaps_update_ts = cur_ts
        price_deltas = self._get_price_deltas()
        for interval in self._intervals:
            cur_treemap = copy.deepcopy(self._base_treemap)
            for sector in cur_treemap["children"]:
                for ticker_data in sector["children"]:
                    ticker = ticker_data["ticker"]
                    ticker_data["price_delta"] = price_deltas[interval][ticker]
            self._treemaps[interval] = cur_treemap
        self._save_treemaps()

    def _update_containers(self, trade: TradeEvent):
        for period in self._intervals:
            self._containers[period][trade.instrument].insert(
                trade.price, trade.time.timestamp()
            )

    def on_trade(self, trade: TradeEvent):
        self._update_containers(trade)
        self._update_treemaps()  
