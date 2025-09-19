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

    # cookies = [
    #     {
    #         "domain": ".backend.wplace.live",
    #         "expires": 2000000000,
    #         "httpOnly": True,
    #         "name": "j",
    #         "path": "/",
    #         "priority": "Medium",
    #         "sameParty": False,
    #         "sameSite": "Lax",
    #         "secure": True,
    #         "session": False,
    #         "size": 250,
    #         "sourcePort": 443,
    #         "sourceScheme": "Secure",
    #         "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjgwOTgzNTAsInNlc3Npb25JZCI6Im9tLWhIMVhmV2dlSUg3SmtTU2pxQS1WdW8wYTdlZnJ4ek1NR3VyQ3RENzA9IiwiaXNzIjoid3BsYWNlIiwiZXhwIjoxNzU5NDM0OTIyLCJpYXQiOjE3NTgxMzg5MjJ9.iRPi7jGy2Ba6OhSx6SEejmnpIvtWroYM4G158O7JwMM",
    #     },
    # ]
    print(cookies)
    sys.exit(0)
    sb.execute_cdp_cmd("Storage.setCookies", {"cookies": cookies})

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
