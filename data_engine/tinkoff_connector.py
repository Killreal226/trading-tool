from typing import List

import asyncio

from tinkoff.invest import (
    AsyncClient,
    TradeInstrument,
)
from tinkoff.invest.async_services import AsyncMarketDataStreamManager

from .events import TradeEvent


class TinkoffConnector:

    def __init__(self, config) -> None:
        self._config = config
        self._token : str = config["token"]
        self._queue : asyncio.Queue = None

    def _listen_trades_done_callback(self, fut):
        exc = fut.exception()
        if exc:
            raise exc

    def run(self) -> None:
        task = asyncio.ensure_future(self._listen_trades())
        task.add_done_callback(self._listen_trades_done_callback)

    def _get_instruments_to_subscribe(self):
        result = []
        for i in self._config["instruments"]:
            result.append(TradeInstrument(figi=self._config["ticker_to_figi"][i]))
        return result

    async def _listen_trades(self) -> None:
        async with AsyncClient(self._token) as client:
            market_data_stream: AsyncMarketDataStreamManager = (
                client.create_market_data_stream()
            )
            market_data_stream.trades.subscribe(
               self._get_instruments_to_subscribe()
            )
            async for marketdata in market_data_stream:
                if marketdata.trade:
                    trade = marketdata.trade
                    await self._queue.put(TradeEvent(
                        self._config["figi_to_ticker"][trade.figi], trade.time,
                        trade.direction, trade.price, trade.quantity
                    ))

    def set_queue(self, queue: asyncio.Queue) -> None: 
        self._queue = queue
