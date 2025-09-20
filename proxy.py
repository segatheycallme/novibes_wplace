import json
from typing import Callable

from mitmproxy.http import HTTPFlow
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from pixel_calc import get_pixels, todo_pixels

capabilities = {}


class CustomAddon:
    def response(self, flow: HTTPFlow) -> None:
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
                    data = data | get_pixels(caps["charges"], caps["colors_bitmap"])

                    path_split = flow.request.path.split("/")
                    path_split[-1] = str(data["ty"])
                    path_split[-2] = str(data["tx"])
                    flow.request.path = "/".join(path_split)

                flow.request.set_text(json.dumps(data))
                print(data)
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
