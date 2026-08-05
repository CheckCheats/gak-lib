import subprocess, json, sys, time

EXE = r"C:\Users\CARSER\AppData\Local\Real\data\mcp\real-mcp.exe"

proc = subprocess.Popen(
    [EXE],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
)

def send(obj):
    line = json.dumps(obj)
    proc.stdin.write(line + "\n")
    proc.stdin.flush()

def read_lines(timeout=8):
    out = []
    end = time.time() + timeout
    while time.time() < end:
        line = proc.stdout.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            out.append({"raw": line})
        # stop once we have a tools/list result or enough
        return out
    return out

# 1. initialize
init_id = "1"
send({
    "jsonrpc": "2.0",
    "id": init_id,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "probe", "version": "1.0"}
    }
})

# read initialize response
time.sleep(1)
init_resp = proc.stdout.readline().strip()
print("INIT:", init_resp[:2000])

# 2. initialized notification
send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

# 3. tools/list
send({"jsonrpc": "2.0", "id": "2", "method": "tools/list", "params": {}})

# read until we get tools/list result
time.sleep(1.5)
resp = proc.stdout.readline().strip()
print("TOOLS_LIST_RAW:", resp[:4000])

# Also try resources/list
send({"jsonrpc": "2.0", "id": "3", "method": "resources/list", "params": {}})
time.sleep(1)
r2 = proc.stdout.readline().strip()
print("RESOURCES_RAW:", r2[:2000])

try:
    proc.terminate()
except Exception:
    pass
