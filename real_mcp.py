import subprocess, json, sys, time

EXE = r"C:\Users\CARSER\AppData\Local\Real\data\mcp\real-mcp.exe"

proc = subprocess.Popen(
    [EXE],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
    encoding="utf-8",
)

def send(obj):
    proc.stdin.write(json.dumps(obj) + "\n")
    proc.stdin.flush()

# initialize
send({"jsonrpc":"2.0","id":"init","method":"initialize",
      "params":{"protocolVersion":"2024-11-05","capabilities":{},
                "clientInfo":{"name":"cli","version":"1.0"}}})
time.sleep(0.8)
# consume init response + any early logs
def drain(timeout=2.0):
    end = time.time()+timeout
    while time.time()<end:
        line = proc.stdout.readline()
        if not line: break
        line=line.strip()
        if line: return line
    return ""

init = drain()
print("INIT_OK" if '"result"' in init else "INIT_FAIL", init[:300])

send({"jsonrpc":"2.0","method":"notifications/initialized","params":{}})

def call(tool, args, cid="c1"):
    send({"jsonrpc":"2.0","id":cid,"method":"tools/call",
          "params":{"name":tool,"arguments":args}})
    # read until we get a response with this id (skip notifications)
    end = time.time()+25
    while time.time()<end:
        line = proc.stdout.readline()
        if not line: 
            time.sleep(0.1); continue
        line=line.strip()
        if not line: continue
        try:
            msg=json.loads(line)
        except Exception:
            continue
        if msg.get("id")==cid:
            return msg
        # else it's a notification/log; ignore
    return {"error":"timeout"}

TOOL = sys.argv[1] if len(sys.argv)>1 else "get-game-info"
ARGS = json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
res = call(TOOL, ARGS)
# pretty print text content
if "result" in res:
    content = res["result"].get("content",[])
    for c in content:
        if c.get("type")=="text":
            print(c["text"])
        else:
            print(json.dumps(c, ensure_ascii=False)[:3000])
elif "error" in res:
    print("TOOL_ERROR:", json.dumps(res["error"], ensure_ascii=False)[:2000])
else:
    print(json.dumps(res, ensure_ascii=False)[:3000])

try: proc.terminate()
except Exception: pass
