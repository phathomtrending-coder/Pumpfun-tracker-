import asyncio

from bot import scan_for_new_tokens, check_multipliers

async def main():
    await scan_for_new_tokens()
    await check_multipliers()

if __name__ == "__main__":
    asyncio.run(main())
