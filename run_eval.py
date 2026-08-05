import subprocess, json, sys, time

EXE = r"C:\Users\CARSER\AppData\Local\Real\data\mcp\real-mcp.exe"

proc = subprocess.Popen(
    [EXE], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    text=True, bufsize=1, encoding="utf-8",
)

def send(obj):
    proc.stdin.write(json.dumps(obj) + "\n")
    proc.stdin.flush()

send({"jsonrpc":"2.0","id":"init","method":"initialize",
      "params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"cli","version":"1.0"}}})
time.sleep(0.8)
def drain(t=1.5):
    end=time.time()+t
    while time.time()<end:
        l=proc.stdout.readline()
        if not l: break
        l=l.strip()
        if l: return l
    return ""
drain()

send({"jsonrpc":"2.0","method":"notifications/initialized","params":{}})

tool = sys.argv[1] if len(sys.argv)>1 else "eval"
if tool=="eval" and len(sys.argv)>2 and sys.argv[2]=="--file":
    code = open(sys.argv[3], encoding="utf-8").read()
    args = {"expression": code}
elif tool=="get-data-by-code" and len(sys.argv)>2 and sys.argv[2]=="--file":
    code = open(sys.argv[3], encoding="utf-8").read()
    args = {"code": code}
else:
    args = json.loads(sys.argv[2]) if len(sys.argv)>2 else {}

def call(t, a, cid="c1"):
    send({"jsonrpc":"2.0","id":cid,"method":"tools/call","params":{"name":t,"arguments":a}})
    end=time.time()+30
    while time.time()<end:
        l=proc.stdout.readline()
        if not l: time.sleep(0.1); continue
        l=l.strip()
        if not l: continue
        try: msg=json.loads(l)
        except Exception: continue
        if msg.get("id")==cid: return msg
    return {"error":"timeout"}

res = call(tool, args)
if "result" in res:
    for c in res["result"].get("content",[]):
        if c.get("type")=="text":
            print(c["text"])
        else:
            print(json.dumps(c, ensure_ascii=False)[:4000])
elif "error" in res:
    print("TOOL_ERROR:", json.dumps(res["error"], ensure_ascii=False)[:3000])
else:
    print(json.dumps(res, ensure_ascii=False)[:4000])
try: proc.terminate()
except Exception: pass
