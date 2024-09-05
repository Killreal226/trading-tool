import asyncio

from .events import TradeEvent

class Engine:

    def __init__(self, connector, treemap_handler) -> None:
        self._connector = connector
        self._treemap_handler = treemap_handler
        self._events = asyncio.Queue()
        self._connector.set_queue(self._events)

    async def run(self) -> None:
        self._connector.run()
        await self._process_events_queue()

    async def _process_events_queue(self) -> None:
        while True:
            event = await self._events.get()
            if isinstance(event, TradeEvent):
                self._treemap_handler.on_trade(event)
            else:
                raise RuntimeError("Can't process unknown event type")
