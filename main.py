import asyncio

import browser
import proxy
import pixel_calc

URL = "https://wplace.live/"
PROXY = "localhost:8080"


async def main():
    # load image
    pixel_calc.todo_pixels

    # data parsing and logging in
    cookies = browser.get_cookies()

    await asyncio.gather(proxy.run(), asyncio.to_thread(browser.run, cookies))


if __name__ == "__main__":
    asyncio.run(main())
