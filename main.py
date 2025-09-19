import sys
from selenium.webdriver.common.keys import Keys
from seleniumbase import SB

URL = "https://wplace.live/"


# account parsing (plaintext rlly bad)
accounts = []

with open("plaintext_info") as file:
    accounts_str = file.read()
    for i in accounts_str.split(";"):
        accounts.append(i.split(":"))
    if accounts[-1] == ["\n"]:
        accounts.pop()
print(f"\n{len(accounts)} account(s) added")


def get_cookies(user, password, sb) -> str | None:
    sb.execute_cdp_cmd("Storage.clearCookies", {})

    sb.open(URL)

    sb.click("//button[text()='Log in']")

    # captcha
    sb.sleep(4)
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
    sb.execute_cdp_cmd("Storage.clearCookies", {})  # possibly useless
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
    sb.sleep(1)
    sb.refresh()

    # captcha
    sb.sleep(4)
    sb.click(".z-100")

    sb.click("div.absolute.bottom-3.left-1\\/2.z-30.-translate-x-1\\/2")
    sb.click_with_offset("body", 200, 200)  # somewhere on canvas
    sb.click("div.absolute.bottom-0.left-1\\/2.-translate-x-1\\/2")


with SB(uc=True, headed=True, proxy="localhost:8080") as sb:
    # init
    sb.open(URL)

    sb.execute_script(
        'localStorage.setItem("location",\'{"lng":20.64382364844073,"lat":43.11796421702974,"zoom":16.660873669103147}\')'
    )

    cookies = []
    for acc in accounts:
        cookie = get_cookies(acc[0], acc[1], sb)
        if cookie is None:
            print(f"Failed to login user: {acc[0]}; skipping!")
            continue
        cookies.append(cookie)

    for cookie in cookies:
        paint_pixel(cookie, sb)

    sb.sleep(1)
