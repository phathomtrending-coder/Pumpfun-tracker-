import asyncio

from posters import post_test_message
from bot import scan_for_new_tokens, check_multipliers

async def main():
    await post_test_message()
    await scan_for_new_tokens()
    await check_multipliers()

if __name__ == "__main__":
    asyncio.run(main())
