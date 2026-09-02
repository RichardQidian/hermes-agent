#!/usr/bin/env python3
"""浏览器内 WebSocket 连通性测试（PNA 诊断）：若 10s 无回调(state=0) = PNA 挂起，需加 Chrome flag。"""
import asyncio, json, urllib.request
import websockets

async def main():
    with urllib.request.urlopen("http://127.0.0.1:9222/json") as f:
        targets = json.load(f)
    page = next(t for t in targets if t["type"] == "page")
    CDP = page["webSocketDebuggerUrl"]
    async with websockets.connect(CDP, max_size=2**24) as ws:
        mid = 0
        async def cmd(method, params=None):
            nonlocal mid
            mid += 1
            await ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == mid:
                    return msg
        r = await cmd("Runtime.evaluate", {
            "expression": """(() => {
              return new Promise(res => {
                const results = {};
                const ws = new WebSocket('ws://127.0.0.1:60832/eda');
                ws.onopen = () => { results.open = 'OPEN'; ws.close(); setTimeout(() => res(JSON.stringify(results)), 300); };
                ws.onerror = () => { results.error = 'onerror'; };
                ws.onclose = (e) => { results.close = 'code=' + e.code; setTimeout(() => res(JSON.stringify(results)), 300); };
                setTimeout(() => { results.timeout = '10s no result, state=' + ws.readyState; res(JSON.stringify(results)); }, 10000);
              });
            })()""",
            "returnByValue": True, "awaitPromise": True
        })
        print("WS TEST:", r["result"]["result"]["value"])
        # OPEN = daemon 可达；state=0 挂起 = PNA 限制（检查 Chrome flag）

asyncio.run(main())
