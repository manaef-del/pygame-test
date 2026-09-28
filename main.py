"""Einstiegspunkt: ``python main.py`` (nativ) oder ``pygbag .`` (Browser)."""

import asyncio

from game.app import run

if __name__ == "__main__":
    asyncio.run(run())
