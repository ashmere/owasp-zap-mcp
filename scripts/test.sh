#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ZAP_URL="http://localhost:8080"
MCP_URL="http://localhost:3000"
TIMEOUT=30

echo -e "${BLUE}🧪 OWASP ZAP MCP Test Suite${NC}"
echo "=================================="
echo ""

# Function to print test results
print_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"

    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✅ $test_name: PASS${NC}"
        if [ -n "$details" ]; then
            echo -e "   ${details}"
        fi
    else
        echo -e "${RED}❌ $test_name: FAIL${NC}"
        if [ -n "$details" ]; then
            echo -e "   ${RED}$details${NC}"
        fi
    fi
    echo ""
}

# Function to check if a URL is accessible
check_url() {
    local url="$1"
    local timeout="$2"

    if curl -s --max-time "$timeout" "$url" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check JSON response
check_json_response() {
    local url="$1"
    local expected_field="$2"
    local timeout="$3"

    local response=$(curl -s --max-time "$timeout" "$url" 2>/dev/null)
    if echo "$response" | jq -e ".$expected_field" >/dev/null 2>&1; then
        echo "$response"
        return 0
    else
        echo "$response"
        return 1
    fi
}

# Function to test MCP tool call
test_mcp_tool() {
    local tool_name="$1"
    local session_id="test-session-$(date +%s)"

    # First, establish SSE connection to get endpoint
    local sse_response=$(curl -s --max-time 5 "$MCP_URL/sse" 2>/dev/null | head -n 1)
    if [[ "$sse_response" =~ session_id=([a-f0-9-]+) ]]; then
        session_id="${BASH_REMATCH[1]}"
    fi

    # Prepare MCP tool call payload
    local payload=$(cat <<EOF
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "$tool_name",
        "arguments": {}
    }
}
EOF
)

    # Call the tool via MCP
    local response=$(curl -s --max-time "$TIMEOUT" \
        -H "Content-Type: application/json" \
        -X POST \
        -d "$payload" \
        "$MCP_URL/mcp/messages?session_id=$session_id" 2>/dev/null)

    echo "$response"
}

# Test 1: Check if Docker is running
echo -e "${YELLOW}Test 1: Docker Service${NC}"
if docker info >/dev/null 2>&1; then
    print_result "Docker Service" "PASS" "Docker is running"
else
    print_result "Docker Service" "FAIL" "Docker is not running or not accessible"
    exit 1
fi

# Test 2: Check if ZAP container is running
echo -e "${YELLOW}Test 2: ZAP Container Status${NC}"
if docker compose ps zap | grep -q "Up"; then
    container_status=$(docker compose ps zap | grep zap | awk '{print $4}')
    print_result "ZAP Container" "PASS" "Container status: $container_status"
else
    print_result "ZAP Container" "FAIL" "ZAP container is not running"
    echo -e "${YELLOW}💡 Tip: Run './scripts/rebuild.sh' to start ZAP${NC}"
    exit 1
fi

# Test 3: Check ZAP API accessibility
echo -e "${YELLOW}Test 3: ZAP API Accessibility${NC}"
if check_url "$ZAP_URL" "$TIMEOUT"; then
    print_result "ZAP API Access" "PASS" "ZAP API is accessible at $ZAP_URL"
else
    print_result "ZAP API Access" "FAIL" "Cannot reach ZAP API at $ZAP_URL"
    exit 1
fi

# Test 4: Check ZAP API version endpoint
echo -e "${YELLOW}Test 4: ZAP API Version${NC}"
zap_version_response=$(check_json_response "$ZAP_URL/JSON/core/view/version/" "version" "$TIMEOUT")
if [ $? -eq 0 ]; then
    zap_version=$(echo "$zap_version_response" | jq -r '.version')
    print_result "ZAP API Version" "PASS" "ZAP version: $zap_version"
else
    print_result "ZAP API Version" "FAIL" "Cannot get ZAP version: $zap_version_response"
    exit 1
fi

# Test 5: Check if MCP server is running
echo -e "${YELLOW}Test 5: MCP Server Status${NC}"
if check_url "$MCP_URL/health" "$TIMEOUT"; then
    print_result "MCP Server Access" "PASS" "MCP server is accessible at $MCP_URL"
else
    print_result "MCP Server Access" "FAIL" "Cannot reach MCP server at $MCP_URL"
    echo -e "${YELLOW}💡 Tip: Start MCP server with 'docker compose --profile security up -d'${NC}"
    exit 1
fi

# Test 6: Check MCP server health endpoint
echo -e "${YELLOW}Test 6: MCP Server Health${NC}"
mcp_health_response=$(check_json_response "$MCP_URL/health" "status" "$TIMEOUT")
if [ $? -eq 0 ]; then
    mcp_status=$(echo "$mcp_health_response" | jq -r '.status')
    mcp_server=$(echo "$mcp_health_response" | jq -r '.server // "Unknown"')
    if [ "$mcp_status" = "healthy" ]; then
        print_result "MCP Server Health" "PASS" "Server: $mcp_server, Status: $mcp_status"
    else
        print_result "MCP Server Health" "FAIL" "Server status: $mcp_status"
        exit 1
    fi
else
    print_result "MCP Server Health" "FAIL" "Invalid health response: $mcp_health_response"
    exit 1
fi

# Test 7: Check MCP server status and tools
echo -e "${YELLOW}Test 7: MCP Server Tools${NC}"
mcp_status_response=$(check_json_response "$MCP_URL/status" "tools" "$TIMEOUT")
if [ $? -eq 0 ]; then
    tool_count=$(echo "$mcp_status_response" | jq '.tools | length')
    tools_list=$(echo "$mcp_status_response" | jq -r '.tools | join(", ")')
    print_result "MCP Server Tools" "PASS" "Found $tool_count tools: $tools_list"
else
    print_result "MCP Server Tools" "FAIL" "Cannot get tools list: $mcp_status_response"
    exit 1
fi

# Test 8: Test MCP Tool Availability
echo -e "${YELLOW}Test 8: MCP Tool Availability${NC}"
echo "   Verifying MCP tools are properly registered..."

# Test that the zap_health_check tool is available and the MCP server can list it
if echo "$tools_list" | grep -q "zap_health_check"; then
    print_result "MCP Tool Availability" "PASS" "zap_health_check tool is registered and available"
else
    print_result "MCP Tool Availability" "FAIL" "zap_health_check tool not found in available tools"
    exit 1
fi

# Test 8b: MCP Server Response Test
echo -e "${YELLOW}Test 8b: MCP Server Response Test${NC}"
echo "   Testing MCP server responsiveness..."

# Test that the MCP server can handle basic requests
mcp_ping_response=$(curl -s --max-time 5 "$MCP_URL/health" 2>/dev/null)
if echo "$mcp_ping_response" | jq -e '.status' >/dev/null 2>&1; then
    print_result "MCP Server Response" "PASS" "MCP server responds to health checks"
else
    print_result "MCP Server Response" "FAIL" "MCP server not responding properly"
    exit 1
fi

# Test 9: Integration test - verify ZAP is accessible from MCP container
echo -e "${YELLOW}Test 9: MCP-ZAP Integration${NC}"

# Detect which MCP container is running
mcp_container=""
if docker compose ps | grep -q "owasp-zap-mcp-build"; then
    mcp_container="owasp-zap-mcp-build"
elif docker compose ps | grep -q "owasp-zap-mcp-image"; then
    mcp_container="owasp-zap-mcp-image"
fi

if [ -n "$mcp_container" ]; then
    echo "   Testing with container: $mcp_container"
    # Test ZAP connectivity from within MCP container
    zap_connectivity=$(docker compose exec -T "$mcp_container" curl -s --max-time 5 http://zap:8080/JSON/core/view/version/ 2>/dev/null || echo "failed")
    if echo "$zap_connectivity" | jq -e '.version' >/dev/null 2>&1; then
        zap_version_from_mcp=$(echo "$zap_connectivity" | jq -r '.version')
        print_result "MCP-ZAP Integration" "PASS" "MCP can reach ZAP (version: $zap_version_from_mcp) via container: $mcp_container"
    else
        print_result "MCP-ZAP Integration" "FAIL" "MCP cannot reach ZAP container"
        echo -e "${RED}   Response: $zap_connectivity${NC}"
        exit 1
    fi
else
    print_result "MCP-ZAP Integration" "FAIL" "No MCP container found (checked: owasp-zap-mcp-build, owasp-zap-mcp-image)"
    echo -e "${YELLOW}💡 Tip: Start with 'docker compose --profile security up -d'${NC}"
    exit 1
fi

# Summary
echo -e "${GREEN}🎉 All tests passed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Test Summary:${NC}"
echo "  • ZAP API: $ZAP_URL (version: $zap_version)"
echo "  • MCP Server: $MCP_URL (status: healthy)"
echo "  • Available Tools: $tool_count"
echo "  • Integration: MCP ↔ ZAP communication working"
echo ""
echo -e "${GREEN}✅ OWASP ZAP MCP is ready for security scanning!${NC}"
 