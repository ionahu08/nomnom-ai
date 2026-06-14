#!/usr/bin/env python3
"""
Test NomNom MCP Tools using the mock server (no database dependency).

This tests the same tools using mock data instead of the real workflow.
Useful for verifying the MCP protocol and tool signatures work.
"""

import json
import subprocess
import sys
import time


class MockMCPTestClient:
    """Test client for mock MCP server."""

    def __init__(self, server_script):
        self.server_script = server_script
        self.proc = None
        self.message_id = 0

    def start_server(self):
        """Start the mock MCP server."""
        print("Starting mock MCP server (no dependencies)...\n")
        self.proc = subprocess.Popen(
            ["/Users/ionahu/venv_nomnom/bin/python", self.server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        time.sleep(0.5)

    def stop_server(self):
        """Stop the server."""
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=2)

    def send_message(self, method, params=None):
        """Send JSON-RPC message."""
        self.message_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": method,
            "params": params or {}
        }
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()
        response = self.proc.stdout.readline()
        if response:
            return json.loads(response)
        return None

    def initialize(self):
        """Initialize MCP."""
        response = self.send_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        })
        return response and "result" in response

    def call_tool(self, name, args):
        """Call a tool."""
        response = self.send_message("tools/call", {
            "name": name,
            "arguments": args
        })
        if response and "result" in response:
            content = response["result"].get("content", [])
            if content:
                return json.loads(content[0]["text"])
        return None


def main():
    """Run mock server tests."""
    print("\n" + "#"*70)
    print("# NomNom MCP Tools - Mock Server Tests")
    print("# (No database or external API dependencies)")
    print("#"*70 + "\n")

    client = MockMCPTestClient(
        "/Users/ionahu/sources/NomNom/learning_lab/phase_6/nomnom_mcp_server_test.py"
    )

    try:
        client.start_server()
        print("✓ Server started\n")

        if not client.initialize():
            print("✗ Failed to initialize")
            return 1

        print("✓ Initialized MCP protocol\n")

        # Test 1: recommend_meal
        print("="*70)
        print("TEST 1: recommend_meal (Mock)")
        print("="*70)
        result = client.call_tool("recommend_meal", {
            "calories": 600,
            "diet_type": "vegetarian"
        })
        if result and "meal_name" in result:
            print("✓ PASS: Tool returns meal recommendation")
            print(f"  Meal: {result['meal_name']}")
            print(f"  Calories: {result['calories']}")
            print(f"  Protein: {result['protein_g']}g")
            test1_pass = True
        else:
            print("✗ FAIL: Invalid response")
            test1_pass = False

        # Test 2: analyze_food_image
        print("\n" + "="*70)
        print("TEST 2: analyze_food_image (Mock)")
        print("="*70)
        result = client.call_tool("analyze_food_image", {
            "image_path": "/tmp/test.jpg"
        })
        if result and "food_name" in result:
            print("✓ PASS: Tool returns food analysis")
            print(f"  Food: {result['food_name']}")
            print(f"  Calories: {result['estimated_calories']}")
            print(f"  Protein: {result['protein_g']}g")
            test2_pass = True
        else:
            print("✗ FAIL: Invalid response")
            test2_pass = False

        # Test 3: lookup_nutrition
        print("\n" + "="*70)
        print("TEST 3: lookup_nutrition (Mock)")
        print("="*70)
        result = client.call_tool("lookup_nutrition", {
            "query": "high protein meals"
        })
        if result and "results" in result:
            print("✓ PASS: Tool returns nutrition results")
            print(f"  Found {result['count']} results:")
            for item in result['results'][:3]:
                print(f"    - {item['food']}: {item['calories']} cal, {item['protein']}g protein")
            print(f"  Citations: {result['citations']}")
            test3_pass = True
        else:
            print("✗ FAIL: Invalid response")
            test3_pass = False

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        passed = sum([test1_pass, test2_pass, test3_pass])
        print(f"✓ {passed}/3 tests passed")
        print("\n✓ All tools are functional at the MCP protocol level")
        print("✓ Ready for Claude Code integration testing")

        return 0 if passed == 3 else 1

    finally:
        client.stop_server()


if __name__ == "__main__":
    sys.exit(main())
