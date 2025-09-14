import subprocess
import json
import threading

# Path to run MCP server (assumes uv is installed and aws-pricing-mcp-server available)
#MCP_CMD = ["uv", "tool", "run", "--from", "awslabs.aws-pricing-mcp-server@latest"]
MCP_CMD = [
    "uv", "tool", "run", "--from", "awslabs.aws-pricing-mcp-server@latest",
    "awslabs.aws-pricing-mcp-server"
]


def read_output(proc):
    """Read output from MCP server continuously."""
    for line in iter(proc.stdout.readline, b''):
        if line:
            print("<<<", line.decode().strip())

def main():
    # Start MCP server as subprocess
    proc = subprocess.Popen(
        MCP_CMD,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
        text=True
    )

    # print any immediate errors
    err = proc.stderr.read(5)
    if err:
        print("⚠️ Server error:", err)

    # Start thread to read output
    threading.Thread(target=read_output, args=(proc,), daemon=True).start()

    # Send "initialize" message
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-05-01",
            "clientInfo": {
                "name": "python-client",
                "version": "0.1"
            }
        }
    }

    proc.stdin.write((json.dumps(init_msg) + "\n").encode())
    proc.stdin.flush()

    # Example pricing request: Get On-Demand m5.large Linux in N. Virginia
    pricing_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/execute",
        "params": {
            "name": "getProducts",
            "arguments": {
                "ServiceCode": "AmazonEC2",
                "Filters": [
                    {"Type": "TERM_MATCH", "Field": "instanceType", "Value": "m5.large"},
                    {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
                    {"Type": "TERM_MATCH", "Field": "location", "Value": "US East (N. Virginia)"}
                ],
                "MaxResults": 1
            }
        }
    }

    proc.stdin.write((json.dumps(pricing_request) + "\n").encode())
    proc.stdin.flush()

if __name__ == "__main__":
    main()