#!/usr/bin/env python3
"""开启连接器的「允许外部交互」权限（IndexedDB 布尔）。连接器 UUID: 4dae27407c1d43be98e8e210d45fe587"""
import asyncio, json, urllib.request
import websockets

UUID = "4dae27407c1d43be98e8e210d45fe587"
DB = "User_3116397b71b24e71bf35aca8196f9de1_v6"  # teamUuid 变化时用 easyeda project info 取

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
            "expression": f"""(() => {{
              return new Promise(res => {{
                const req = indexedDB.open('{DB}');
                req.onsuccess = () => {{
                  const db = req.result;
                  const tx = db.transaction('extensionsIndex', 'readwrite');
                  const os = tx.objectStore('extensionsIndex');
                  const get = os.get('{UUID}');
                  get.onsuccess = () => {{
                    const rec = get.result;
                    if (!rec) {{ res('record not found'); return; }}
                    rec.isAllowExternalInteractions = true;
                    rec.isEnable = true;
                    os.put(rec);
                    tx.oncomplete = () => res('updated: allow=' + rec.isAllowExternalInteractions + ' enable=' + rec.isEnable);
                  }};
                }};
                req.onerror = () => res('open err');
              }});
            }})()""",
            "returnByValue": True, "awaitPromise": True
        })
        print(r["result"]["result"]["value"])
        print("改完必须刷新页面(Page.reload)让连接器读取新权限")

asyncio.run(main())
