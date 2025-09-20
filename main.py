from seleniumbase import SB

import browser

URL = "https://wplace.live/"
PROXY = "localhost:8080"


def main():
    # data parsing
    cookies = browser.get_cookies()

    with SB(uc=True, headed=True, proxy=PROXY) as sb:
        # set location (not needed)
        sb.open(URL)
        sb.execute_script(
            'localStorage.setItem("location",\'{"lng":20.64382364844073,"lat":43.11796421702974,"zoom":16.660873669103147}\')'
        )

        # TODO: 15 min timer loop here
        for cookie in cookies:
            browser.paint_pixel(cookie, sb)

        print("Done!")
        sb.sleep(5)


if __name__ == "__main__":
    main()
