#!/usr/bin/env python3
"""导航 pro.lceda.cn/editor 并验证登录态。用法: python3 cdp_reopen.py [url]"""
import asyncio, json, sys, urllib.request
import websockets

URL = sys.argv[1] if len(sys.argv) > 1 else "https://pro.lceda.cn/editor"

async def main():
    for _ in range(15):
        try:
            with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=2) as f:
                targets = json.load(f)
            break
        except Exception:
            await asyncio.sleep(1)
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
        await cmd("Page.enable")
        await cmd("Page.navigate", {"url": URL})
        await asyncio.sleep(12)
        r = await cmd("Runtime.evaluate", {
            "expression": "({href: location.href, title: document.title, loggedIn: !(document.body.innerText.includes('Login') && document.body.innerText.includes('Register'))})",
            "returnByValue": True
        })
        print(json.dumps(r["result"]["result"]["value"], ensure_ascii=False))

asyncio.run(main())
