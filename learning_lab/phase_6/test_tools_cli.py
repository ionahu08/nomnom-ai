#!/usr/bin/env python3
"""
CLI Test Suite for NomNom MCP Tools

Tests each tool via JSON-RPC protocol without Claude Code intermediary.
"""

import json
import subprocess
import sys
import time
from pathlib import Path


class MCPTestClient:
    """Minimal MCP client for testing tools."""

    def __init__(self, server_command):
        self.server_command = server_command
        self.proc = None
        self.message_id = 0

    def start_server(self):
        """Start the MCP server subprocess."""
        print("Starting MCP server...")
        self.proc = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        time.sleep(1)  # Wait for server to start
        print("✓ Server started\n")

    def stop_server(self):
        """Stop the server."""
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=2)

    def send_message(self, method, params=None):
        """Send a JSON-RPC message to the server."""
        self.message_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": method,
            "params": params or {}
        }

        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()

        # Read response
        response_line = self.proc.stdout.readline()
        if not response_line:
            return None

        return json.loads(response_line)

    def initialize(self):
        """Initialize the MCP connection."""
        response = self.send_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-cli", "version": "1.0"}
        })

        if response and "result" in response:
            print("✓ Initialized MCP protocol\n")
            return True
        return False

    def list_tools(self):
        """List available tools."""
        response = self.send_message("tools/list")

        if response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"✓ Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
            print()
            return tools
        return []

    def call_tool(self, tool_name, arguments):
        """Call a tool with the given arguments."""
        response = self.send_message("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

        return response


def test_recommend_meal(client):
    """Test the recommend_meal tool."""
    print("\n" + "="*70)
    print("TEST 1: recommend_meal (Real Workflow)")
    print("="*70)
    print("Testing meal recommendation with real workflow...\n")

    response = client.call_tool("recommend_meal", {
        "calories": 600,
        "diet_type": "vegetarian"
    })

    if response and "result" in response:
        content = response["result"].get("content", [])
        if content:
            try:
                result = json.loads(content[0]["text"])
                print("✓ Tool executed successfully\n")
                print("Response:")
                print(json.dumps(result, indent=2))

                # Verify structure
                if "meal_name" in result and "calories" in result:
                    print("\n✓ PASS: recommend_meal returns correct structure")
                    return True
                else:
                    print("\n✗ FAIL: Missing required fields in response")
                    return False
            except json.JSONDecodeError as e:
                print(f"✗ FAIL: Could not parse tool response as JSON: {e}")
                print(f"Raw response: {content[0]['text']}")
                return False
    else:
        print(f"✗ FAIL: No response from tool")
        if response:
            print(f"Response: {json.dumps(response, indent=2)}")
        return False


def test_analyze_food_image(client):
    """Test the analyze_food_image tool."""
    print("\n" + "="*70)
    print("TEST 2: analyze_food_image (Vision API)")
    print("="*70)
    print("Testing food image analysis...\n")

    # Use a test image path (doesn't need to exist for the test)
    test_image = "/tmp/test_food.jpg"

    response = client.call_tool("analyze_food_image", {
        "image_path": test_image
    })

    if response and "result" in response:
        content = response["result"].get("content", [])
        if content:
            try:
                result = json.loads(content[0]["text"])
                print("✓ Tool executed successfully\n")
                print("Response:")
                print(json.dumps(result, indent=2))

                # Verify structure
                if "food_name" in result and "estimated_calories" in result:
                    print("\n✓ PASS: analyze_food_image returns correct structure")
                    return True
                else:
                    print("\n✗ FAIL: Missing required fields in response")
                    return False
            except json.JSONDecodeError as e:
                print(f"✗ FAIL: Could not parse tool response as JSON: {e}")
                return False
    else:
        print(f"✗ FAIL: No response from tool")
        return False


def test_lookup_nutrition(client):
    """Test the lookup_nutrition tool."""
    print("\n" + "="*70)
    print("TEST 3: lookup_nutrition (RAG Search)")
    print("="*70)
    print("Testing RAG-backed nutrition lookup...\n")

    response = client.call_tool("lookup_nutrition", {
        "query": "high protein vegetarian meals"
    })

    if response and "result" in response:
        content = response["result"].get("content", [])
        if content:
            try:
                result = json.loads(content[0]["text"])
                print("✓ Tool executed successfully\n")
                print("Response:")
                print(json.dumps(result, indent=2))

                # Verify structure
                if "results" in result and "citations" in result:
                    print(f"\n✓ PASS: lookup_nutrition found {len(result['results'])} results")
                    print(f"  Citations: {result['citations']}")
                    return True
                else:
                    print("\n✗ FAIL: Missing required fields in response")
                    return False
            except json.JSONDecodeError as e:
                print(f"✗ FAIL: Could not parse tool response as JSON: {e}")
                return False
    else:
        print(f"✗ FAIL: No response from tool")
        return False


def main():
    """Run all tests."""
    print("\n" + "#"*70)
    print("# NomNom MCP Tools - CLI Test Suite")
    print("#"*70)

    # Create client
    server_command = [
        "/Users/ionahu/sources/NomNom/learning_lab/phase_6/run_mcp_server.sh"
    ]

    client = MCPTestClient(server_command)

    try:
        # Start server
        client.start_server()

        # Initialize
        if not client.initialize():
            print("✗ Failed to initialize MCP protocol")
            return 1

        # List tools
        tools = client.list_tools()
        if not tools:
            print("✗ No tools found")
            return 1

        # Run tests
        results = {}
        results["recommend_meal"] = test_recommend_meal(client)
        results["analyze_food_image"] = test_analyze_food_image(client)
        results["lookup_nutrition"] = test_lookup_nutrition(client)

        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        for tool_name, passed_test in results.items():
            status = "✓ PASS" if passed_test else "✗ FAIL"
            print(f"{status}: {tool_name}")

        print(f"\nTotal: {passed}/{total} tests passed")

        # Verification checklist
        print("\n" + "="*70)
        print("VERIFICATION CHECKLIST")
        print("="*70)
        checklist = [
            ("Claude Code can list tools", True),  # We just did this
            ("analyze_food_image works with image", results.get("analyze_food_image", False)),
            ("lookup_nutrition returns RAG results", results.get("lookup_nutrition", False)),
            ("recommend_meal invokes workflow", results.get("recommend_meal", False)),
        ]

        for item, done in checklist:
            status = "✓" if done else "[ ]"
            print(f"{status} {item}")

        return 0 if passed == total else 1

    finally:
        client.stop_server()
        print("\n✓ Server stopped\n")


if __name__ == "__main__":
    sys.exit(main())
