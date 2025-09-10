from selenium.webdriver.common.keys import Keys
from seleniumbase import SB


def get_cookies(user, password, sb) -> str | None:
    sb.execute_cdp_cmd("Storage.clearCookies", {})

    url = "https://wplace.live/"
    sb.open(url)

    sb.click("//button[text()='Log in']")

    sb.sleep(3)
    sb.uc_gui_click_captcha()
    sb.sleep(1)

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


with SB(uc=True, headed=True, proxy="localhost:8080") as sb:
    url = "https://wplace.live/"

    cookies = [
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
            "size": 250,
            "sourcePort": 443,
            "sourceScheme": "Secure",
            "value": "",
        },
    ]
    sb.execute_cdp_cmd("Storage.setCookies", {"cookies": cookies})

    sb.open(url)
    sb.execute_script(
        'localStorage.setItem("location",\'{"lng":20.64382364844073,"lat":43.11796421702974,"zoom":16.660873669103147}\')'
    )
    sb.sleep(1)
    sb.refresh()

    # captcha
    sb.sleep(5)
    # dogshit tailwind ily ily ily ily
    sb.click(".z-100")
    sb.sleep(1)

    sb.click("div.absolute.bottom-3.left-1\\/2.z-30.-translate-x-1\\/2")
    sb.click_with_offset("body", 200, 200)
    sb.click("div.absolute.bottom-0.left-1\\/2.-translate-x-1\\/2")

    # print(get_cookies("segq3.k", "sddMake008", sb))

    input()
    print(":3")

    sb.sleep(500)
