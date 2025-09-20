import asyncio

import browser
import proxy
import pixel_calc

URL = "https://wplace.live/"
PROXY = "localhost:8080"


async def main():
    # load image
    todo_pixels = pixel_calc.generate_pixels("smile.png", 1141, 751, 420, 620)

    # data parsing and logging in
    cookies = browser.get_cookies()

    await asyncio.gather(
        proxy.run(todo_pixels), asyncio.to_thread(browser.run, cookies)
    )


if __name__ == "__main__":
    asyncio.run(main())
