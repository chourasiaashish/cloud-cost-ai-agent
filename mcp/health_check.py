import subprocess
import json

# Command to start AWS Pricing MCP Server
MCP_CMD = [
    "uv", "tool", "run", "--from", "awslabs.aws-pricing-mcp-server@latest",
    "awslabs.aws-pricing-mcp-server"
]

def main():
    # Start MCP server as subprocess
    proc = subprocess.Popen(
        MCP_CMD,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,   # use str instead of bytes
        bufsize=1
    )

    # JSON-RPC "initialize" request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }

    # JSON-RPC requires Content-Length headers
    body = json.dumps(request)
    message = f"Content-Length: {len(body)}\r\n\r\n{body}"

    # Send request
    proc.stdin.write(message)
    proc.stdin.flush()

    # Read response
    response = proc.stdout.readline()
    print("Raw response:", response)

    # Keep reading until you see JSON
    while response.strip() == "" or not response.startswith("{"):
        response = proc.stdout.readline()

    try:
        parsed = json.loads(response)
        print("✅ MCP Server responded:", parsed)
    except Exception as e:
        print("⚠️ Could not parse response:", response, e)

    proc.kill()

if __name__ == "__main__":
    main()