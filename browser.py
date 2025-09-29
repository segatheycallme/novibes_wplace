from os.path import isfile

from selenium.webdriver.common.keys import Keys
from seleniumbase import SB

from main import HEADED, PROXY, URL


def run(cookies: list[str]):
    with SB(uc=True, headed=HEADED, proxy=PROXY) as sb:
        # set location (not needed)
        sb.open(URL)
        for cookie in cookies:
            for i in range(3):  # 3 retries
                try:
                    paint_pixel(cookie, sb)
                    break
                except Exception as err:
                    print(f"paint_pixel({i}) failed for user f{cookie}, reason: {err}")
            sb.sleep(7)  # wait for proxy to handle requests


def get_cookies():
    accounts = []
    cookies = []
    if isfile("data/cookies"):
        with open("data/cookies") as file:
            cookies = [cookie.strip() for cookie in file.readlines()]
    else:
        # TODO: not plaintext
        with open("data/accounts") as file:
            accounts_str = file.read()
            for i in accounts_str.split(";"):
                accounts.append(i.split(":"))
            if accounts[-1] == ["\n"]:
                accounts.pop()
        print(f"{len(accounts)} account(s) added")
        with SB(uc=True, headed=True) as sb:
            for acc in accounts:
                cookie = get_cookies_for_acc(acc[0], acc[1], sb)
                if cookie is None:
                    print(f"Failed to login account: {acc[0]}; skipping!")
                    continue
                cookies.append(cookie)

            # update stored cookies
            with open("data/cookies", "w") as file:
                file.write("\n".join(cookies))

    print(f"{len(cookies)} account(s) logged in")
    return cookies


def get_cookies_for_acc(user, password, sb) -> str | None:
    sb.execute_cdp_cmd("Storage.clearCookies", {})

    sb.open(URL)

    sb.click("//button[text()='Log in']")

    # captcha
    sb.sleep(10)
    sb.click(".mt-2.flex.flex-col.items-center.gap-1")

    sb.click("//a[text()=' Login with Google']")

    sb.send_keys("#identifierId", user + Keys.ENTER)
    sb.send_keys("//input[@type='password']", password + Keys.ENTER)

    while "Wplace - Paint the world" != sb.get_title():
        sb.sleep(0.5)

    cookies: list = sb.execute_cdp_cmd("Storage.getCookies", {})["cookies"]
    for cookie in cookies:
        if cookie["domain"] == ".backend.wplace.live" and cookie["name"] == "j":
            return cookie["value"]

    # unable to login?
    return


def paint_pixel(cookie: str, sb):
    # assume already on wplace.live

    # clear old data to avoid detection
    sb.execute_cdp_cmd("Storage.clearCookies", {})
    sb.execute_script("localStorage.clear()")
    sb.execute_script("sessionStorage.clear()")

    sb.execute_script(
        'localStorage.setItem("location",\'{"lng":20.64382364844073,"lat":43.11796421702974,"zoom":16.660873669103147}\')'
    )
    sb.execute_cdp_cmd(
        "Storage.setCookies",
        {
            "cookies": [
                {
                    "domain": ".backend.wplace.live",
                    "expires": 2000000000,
                    "httpOnly": True,
                    "name": "j",
                    "path": "/",
                    "priority": "Medium",
                    "sameParty": False,
                    "sameSite": "Lax",
                    "secure": True,
                    "session": False,
                    "size": len(cookie) + 1,  # ???
                    "sourcePort": 443,
                    "sourceScheme": "Secure",
                    "value": cookie,
                }
            ]
        },
    )
    sb.refresh()

    # clear rules modal (stupid)
    # TODO: unnescessary refresh
    sb.sleep(0.5)
    sb.refresh()

    sb.click_with_offset("body", 200, 200)  # somewhere on canvas
    sb.click("//button[text()=' Paint']")

    # captcha
    sb.sleep(4)
    sb.click(".z-100")

    sb.click("div.absolute.bottom-0.left-1\\/2.-translate-x-1\\/2")
