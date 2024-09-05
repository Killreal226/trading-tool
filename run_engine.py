import asyncio

from data_engine.engine import Engine
from data_engine.treemap_data_handler import TreemapDataHandler
from data_engine.tinkoff_connector import TinkoffConnector
from data_engine.utils import get_config




async def main():
    config = get_config()
    connector = TinkoffConnector(config)
    handler = TreemapDataHandler(config)
    engine = Engine(connector, handler)
    await engine.run()

if __name__ == "__main__":
    asyncio.run(main())
