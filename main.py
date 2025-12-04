import asyncio
import json
import os
from datetime import datetime
from typing import Callable

import yaml
from mitmproxy.http import HTTPFlow
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

import browser
import pixel_calc
from pixel_calc import get_pixels

URL = "https://wplace.live/"
PROXY = "localhost:8080"
HEADED = bool(os.environ.get("NOVIBES_HEADED")) or False
CONFIG = os.environ.get("NOVIBES_CONFIG") or "config.yaml"

todo_pixels = {}
capabilities = {}
mode = "bfs"
skip_transparent = True


async def main():
    load_config()

    # data parsing and logging in
    cookies = browser.get_cookies()

    await asyncio.gather(
        run(), asyncio.to_thread(run_browser, cookies), asyncio.to_thread(main_loop)
    )


def run_browser(cookies):
    browser.run(cookies)


def main_loop():
    while True:
        print("press ENTER to reload config")
        input()
        load_config()


def load_config():
    global todo_pixels, mode, skip_transparent

    # load config
    config = yaml.safe_load(open(CONFIG))
    print("loading config")

    mode = config["mode"] or "bfs"
    skip_transparent = bool(config["skip_transparent"])

    # load images
    todo_pixels = {}
    for image in config["images"]:
        todo_pixels = pixel_calc.dict_union(
            todo_pixels,
            pixel_calc.generate_pixels(
                image["file"], image["tx"], image["ty"], image["px"], image["py"]
            ),
        )
        print(f"added template: {image['name']}")

    pixel_calc.update_pixels(todo_pixels)


class CustomAddon:
    def response(self, flow: HTTPFlow) -> None:
        if (
            flow.request.method == "POST"
            and "https://backend.wplace.live/s0/pixel" in flow.request.url
        ):
            if flow.response is not None:
                now = datetime.now()
                if flow.response.status_code == 200:
                    result = json.loads(flow.response.get_text() or "")
                    log = f"{now} status: painted {result['painted']} pixels\n"
                else:
                    if "[]" in (flow.request.get_text() or ""):
                        log = f"{now} status: no pixels remaining!\n"
                    else:
                        log = f"{now} status: error - {flow.response.status_code} body:{flow.request.get_text()} response:{flow.response.get_text()}\n"

                with open("data/log", "a") as file:
                    file.write(log)
                print(log, end="")
            else:
                print("no response!")
            return

        if "https://backend.wplace.live/me" == flow.request.url:
            try:
                cookies = flow.request.headers.get("cookie")
                if not cookies:
                    return

                j_token = cookies.split("=")[1]
                if flow.response is not None:
                    me = json.loads(flow.response.get_text() or "")
                    capabilities[j_token] = {
                        "charges": me["charges"]["count"],
                        "colors_bitmap": me["extraColorsBitmap"],
                    }
            except Exception as e:
                print(1)
                print(e)

    def request(self, flow: HTTPFlow) -> None:
        try:
            if (
                flow.request.method == "POST"
                and "https://backend.wplace.live/s0/pixel" in flow.request.url
            ):
                j_token = flow.request.headers["cookie"].split("=")[1]
                caps = capabilities.get(j_token)
                if not caps:
                    print(
                        f"Capabilities not found for token: {j_token}, may resolve automatically"
                    )
                    caps = {"charges": 30, "colors_bitmap": 0}
                data = json.loads(flow.request.get_text() or "")

                if len(data["colors"]) == 1:  # dumb check
                    data = data | get_pixels(
                        int(caps["charges"]) - 1,
                        caps["colors_bitmap"],
                        todo_pixels,
                        mode=mode,
                        skip_transparent=skip_transparent,
                    )

                    path_split = flow.request.path.split("/")
                    path_split[-1] = str(data["ty"])
                    path_split[-2] = str(data["tx"])
                    flow.request.path = "/".join(path_split)

                flow.request.set_text(json.dumps(data))
        except Exception as e:
            print(2)
            print(e)


class ProxyServer(DumpMaster):
    def __init__(
        self,
        options: Options = Options(
            listen_host="127.0.0.1",
            listen_port=8080,
            http2=True,
        ),
        loop=None,
        with_termlog=True,
        with_dumper=True,
    ):
        super().__init__(
            options=options,
            loop=loop,
            with_termlog=with_termlog,
            with_dumper=with_dumper,
        )

    async def run(self, on_shutdown: Callable[[Exception], None] | None = None):
        exc: Exception | None = None
        try:
            await DumpMaster.run(self)
        except Exception as e:
            exc = e
            if not callable(on_shutdown):
                raise
        finally:
            if callable(on_shutdown):
                if exc:
                    on_shutdown(exc)
            self.shutdown()


def on_shutdown(exc: Exception | None):
    if not exc:
        return
    print(f"Terminating tasks, cause: {exc}")
    # gracefully close your work


async def run():
    opts = Options(
        listen_host="127.0.0.1",
        listen_port=8080,
        http2=True,
    )
    proxy = ProxyServer(options=opts, with_dumper=False, with_termlog=False)
    proxy.addons.add(
        CustomAddon(),
    )
    await proxy.run(on_shutdown=on_shutdown)


if __name__ == "__main__":
    asyncio.run(main())
