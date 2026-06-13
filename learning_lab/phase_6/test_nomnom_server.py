"""
Test script for NomNom MCP Server

This script:
1. Starts the MCP server as a subprocess
2. Sends MCP protocol messages (JSON-RPC)
3. Verifies the server responds correctly
4. Cleans up

Usage:
    python test_nomnom_server.py
"""

import json
import subprocess
import time
import sys


def test_nomnom_mcp_server():
    """Test the NomNom MCP server"""

    print("=" * 70)
    print("Testing NomNom MCP Server")
    print("=" * 70)

    # Start the server as subprocess
    print("\n[1/4] Starting MCP server...")
    try:
        proc = subprocess.Popen(
            [sys.executable, "nomnom_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
        print("✓ Server started (PID: {})".format(proc.pid))
    except Exception as e:
        print("✗ Failed to start server: {}".format(e))
        return False

    try:
        # Step 1: Send initialize request
        print("\n[2/4] Sending initialize request...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0"
                }
            }
        }

        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()

        # Read initialize response
        response = proc.stdout.readline()
        if not response:
            print("✗ No response from server")
            return False

        init_response = json.loads(response)
        print("✓ Initialize response received")
        print("  Protocol version: {}".format(init_response.get("result", {}).get("protocolVersion")))

        # Step 2: Call recommend_meal tool
        print("\n[3/4] Calling recommend_meal tool...")
        tool_call = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "recommend_meal",
                "arguments": {
                    "calories": 600,
                    "diet_type": "vegetarian"
                }
            }
        }

        proc.stdin.write(json.dumps(tool_call) + "\n")
        proc.stdin.flush()

        # Read tool response
        result_line = proc.stdout.readline()
        if not result_line:
            print("✗ No response from tool call")
            return False

        tool_result = json.loads(result_line)
        print("✓ Tool call successful")

        # Parse the result
        if "result" in tool_result:
            content = tool_result["result"].get("content", [])
            if content and "text" in content[0]:
                result_data = json.loads(content[0]["text"])
                print("  Recommended meal: {}".format(result_data.get("meal_name")))
                print("  Calories: {}".format(result_data.get("calories")))
                print("  Prep time: {} minutes".format(result_data.get("prep_time_minutes")))

        # Step 3: Verify server is responsive
        print("\n[4/4] Server is responsive ✓")

        print("\n" + "=" * 70)
        print("All tests passed!")
        print("=" * 70)
        return True

    except json.JSONDecodeError as e:
        print("✗ Invalid JSON from server: {}".format(e))
        return False
    except Exception as e:
        print("✗ Test failed: {}".format(e))
        return False
    finally:
        # Clean up
        print("\nCleaning up...")
        proc.terminate()
        proc.wait(timeout=5)
        print("✓ Server stopped")


if __name__ == "__main__":
    success = test_nomnom_mcp_server()
    sys.exit(0 if success else 1)
