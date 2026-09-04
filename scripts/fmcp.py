#!/usr/bin/env python3
"""Minimal client for Fusion's built-in MCP server (127.0.0.1:27182)."""
import http.client, json, sys

class Fusion:
    def __init__(self, host="127.0.0.1", port=27182, timeout=180):
        self.c = http.client.HTTPConnection(host, port, timeout=timeout)
        self.H = {"Content-Type":"application/json",
                  "Accept":"application/json, text/event-stream"}
        self._id = 0
        r, _ = self._post({"jsonrpc":"2.0","id":self._next(),"method":"initialize",
            "params":{"protocolVersion":"2025-06-18","capabilities":{},
                      "clientInfo":{"name":"claude-code","version":"2.0"}}})
        self.H["MCP-Session-Id"] = r.getheader("MCP-Session-Id")
        self._post({"jsonrpc":"2.0","method":"notifications/initialized"})
    def _next(self):
        self._id += 1; return self._id
    def _post(self, payload):
        self.c.request("POST","/mcp",json.dumps(payload),self.H)
        r = self.c.getresponse(); return r, r.read().decode()
    def rpc(self, method, params=None):
        _, b = self._post({"jsonrpc":"2.0","id":self._next(),"method":method,"params":params or {}})
        d = json.loads(b)
        if "error" in d: raise RuntimeError(d["error"])
        return d["result"]
    def tools(self):   return self.rpc("tools/list")["tools"]
    def call(self, name, args=None):
        r = self.rpc("tools/call", {"name":name,"arguments":args or {}})
        out = "\n".join(c.get("text","") for c in r.get("content",[]))
        if r.get("isError"): raise RuntimeError(out)
        return out
    def resource(self, uri):
        r = self.rpc("resources/read", {"uri":uri})
        return "\n".join(c.get("text","") for c in r.get("contents",[]))

if __name__ == "__main__":
    f = Fusion()
    if len(sys.argv) == 1:
        for t in f.tools():
            print(f"{t['name']}\n    {(t.get('description') or '').splitlines()[0][:200]}")
    elif sys.argv[1] == "schema":
        for t in f.tools():
            if t["name"] == sys.argv[2]:
                print(json.dumps(t, indent=2))
    elif sys.argv[1] == "res":
        print(f.resource(sys.argv[2])[:6000])
    else:
        print(f.call(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv)>2 else {}))
