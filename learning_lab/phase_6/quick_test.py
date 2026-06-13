import json
import subprocess
import sys

proc = subprocess.Popen(
    ["~/venv_nomnom/bin/python3", "nomnom_mcp_server_test.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    shell=True
)

# Initialize
init = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}
proc.stdin.write(json.dumps(init) + "\n")
proc.stdin.flush()

response = proc.stdout.readline()
if response:
    print("✓ Server initialized")

# Test recommend_meal
tool_call = {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "recommend_meal", "arguments": {"calories": 600, "diet_type": "vegetarian"}}}
proc.stdin.write(json.dumps(tool_call) + "\n")
proc.stdin.flush()

result = proc.stdout.readline()
if result:
    parsed = json.loads(result)
    if "result" in parsed:
        content = json.loads(parsed["result"]["content"][0]["text"])
        print(f"✓ recommend_meal works: {content['meal_name']}")

proc.terminate()
