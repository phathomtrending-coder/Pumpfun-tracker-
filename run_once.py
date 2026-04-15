import asyncio
from bot import scan_for_new_tokens, check_updates

async def main():
    await scan_for_new_tokens()
    await check_updates()

if __name__ == "__main__":
    asyncio.run(main())