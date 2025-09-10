import asyncio
import json
from typing import Callable

from mitmproxy.http import HTTPFlow
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster


class CustomAddon:
    def request(self, flow: HTTPFlow) -> None:
        if (
            flow.request.method == "POST"
            and "https://backend.wplace.live/s0/pixel" in flow.request.url
        ):
            data = json.loads(flow.request.get_text() or "")
            if len(data["colors"]) == 1:
                data["colors"] = [5, 4, 3, 2, 1]
                data["coords"] = [
                    415,
                    628,
                    415,
                    629,
                    415,
                    630,
                    415,
                    631,
                    415,
                    632,
                ]
                # 415, 628,
            flow.request.set_text(json.dumps(data))
            print(data)
            return


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


def matcher(flow: HTTPFlow):
    return "https://www.httpbin.org/" in flow.request.url


async def main():
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


asyncio.run(main())
