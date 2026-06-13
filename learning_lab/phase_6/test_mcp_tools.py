#!/usr/bin/env python3
"""
Test NomNom MCP tools directly (without Claude Code intermediary)

This verifies each tool works before integrating with Claude Code.
"""

import json
import subprocess
import sys
import time


def test_tool(tool_name: str, arguments: dict) -> dict:
    """Call a tool through the MCP server"""

    print(f"\n{'='*70}")
    print(f"Testing: {tool_name}")
    print(f"Arguments: {json.dumps(arguments, indent=2)}")
    print(f"{'='*70}")

    try:
        proc = subprocess.Popen(
            [sys.executable, "nomnom_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # Initialize
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        proc.stdin.write(json.dumps(init_msg) + "\n")
        proc.stdin.flush()
        proc.stdout.readline()  # Read init response

        # Call tool
        tool_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        proc.stdin.write(json.dumps(tool_msg) + "\n")
        proc.stdin.flush()

        # Read result
        result_line = proc.stdout.readline()
        result = json.loads(result_line)

        # Extract content
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"][0]["text"]
            tool_result = json.loads(content)
            print(f"\n✓ Tool executed successfully")
            print(f"Result:\n{json.dumps(tool_result, indent=2)}")
            return tool_result
        else:
            print(f"✗ Unexpected response format")
            return None

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except:
            pass


def main():
    """Run all verification tests"""

    print("\n" + "#"*70)
    print("# NomNom MCP Server - Tool Verification")
    print("#"*70)

    tests = [
        ("recommend_meal", {"calories": 600, "diet_type": "vegetarian"}),
        ("lookup_nutrition", {"query": "high protein vegetarian meals"}),
        ("analyze_food_image", {"image_path": "/tmp/test.jpg"}),  # Will fail but that's OK
    ]

    results = {}
    for tool_name, args in tests:
        result = test_tool(tool_name, args)
        results[tool_name] = "✓ PASS" if result and "error" not in str(result) else "✗ FAIL"

    # Summary
    print(f"\n{'='*70}")
    print("# SUMMARY")
    print(f"{'='*70}")
    for tool_name, status in results.items():
        print(f"{status}: {tool_name}")

    print(f"\n{'='*70}")
    print("Verification Checklist:")
    print("  [1/5] Claude Code can list NomNom tools")
    print("  [2/5] analyze_food_image works with a local photo")
    print("  [3/5] lookup_nutrition returns RAG-backed answers with citations")
    print("  [4/5] recommend_meal invokes the workflow")
    print("  [5/5] Resources can be browsed")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
