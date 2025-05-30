---
description: OWASP ZAP Security Scanning Guidelines and Best Practices
globs: ["**/reports/**", "**/docker-compose.yml", "**/*zap*", "**/*security*"]
alwaysApply: false
---
# OWASP ZAP Security Scanning Rules

## Report Organization
When performing OWASP ZAP security scans, ALWAYS organize reports in subdirectories:

### Directory Structure Requirements
- All scan reports MUST be placed in `reports/{target_domain}/`
- Extract the domain name from the target URL (e.g., `https://example.com/path` → `example.com`)
- Create a subdirectory named after the target domain
- Place ALL report files in this subdirectory

### Required Report Files
For each scan, generate the following reports in the target subdirectory:
1. `{domain}_security_report.html` - Comprehensive HTML report
2. `{domain}_security_report.xml` - XML format report
3. `{domain}_security_report.json` - JSON format report
4. `{domain}_alerts_summary.json` - Detailed alerts data
5. `{domain}_scan_summary.md` - Executive summary with key findings
6. `{domain}_scan_status.md` - Scan completion status and metrics

### Implementation Steps
1. Extract domain from target URL using: `domain=$(echo "$url" | sed 's|https\?://||' | cut -d'/' -f1)`
2. Create `reports/{domain}/` directory
3. Generate all report files with consistent naming
4. Include scan summary with target URL, scan date, alert breakdown, and recommendations

### Naming Convention
- Use domain name for directory (e.g., `example.com`, `api.service.com`)
- Use underscore-separated naming for files (e.g., `example_com_security_report.html`)
- Replace dots with underscores in filenames to avoid confusion
- Keep consistent prefixes based on domain name

### ZAP API Endpoints for Reports
- HTML: `http://localhost:8080/OTHER/core/other/htmlreport/`
- XML: `http://localhost:8080/OTHER/core/other/xmlreport/`
- JSON: `http://localhost:8080/OTHER/core/other/jsonreport/`
- Alerts: `http://localhost:8080/JSON/core/view/alerts/`
- Summary: `http://localhost:8080/JSON/core/view/alertsSummary/`

## Docker Compose Setup

### Available Profiles
The project now supports multiple Docker Compose profiles for different use cases:

#### For Security Engineers (Ready-to-Use)
```bash
# Use pre-built image for immediate scanning
docker-compose --profile services up -d
# OR
docker-compose --profile security up -d
```

#### For Developers
```bash
# Local development with containerized ZAP
docker-compose --profile dev up -d

# Full container development environment
docker-compose --profile devcontainer up -d

# Test container builds from source
docker-compose --profile build-dev up -d
```

### Container Names (Updated)
- **ZAP Container**: `zap` (was `owasp-zap`)
- **MCP Server (Pre-built)**: `owasp-zap-mcp-image` (for services/security profiles)
- **MCP Server (Built)**: `owasp-zap-mcp-build` (for build-dev profile)
- **Dev Container**: `owasp-zap-mcp-devcontainer` (for devcontainer profile)
- **Dev Python**: `owasp-zap-mcp-dev` (for dev profile)

### Platform Compatibility
- **ARM64 Support**: ZAP now uses `platform: linux/amd64` for Apple Silicon compatibility
- **Java Optimization**: Added `JAVA_OPTS=-Xmx1g -XX:+UseContainerSupport` for better performance

ALWAYS use `docker-compose --profile <profile_name> up -d` to start the ZAP environment:
- Ensures proper networking between ZAP and MCP containers
- Provides health checks and proper service dependencies
- Enables API access without authentication issues

NEVER manually start individual ZAP containers - always use the docker-compose.yml configuration.

## MCP Server Configuration

### Current Configuration (SSE Mode)
The MCP server runs in SSE (Server-Sent Events) mode for better integration with modern AI interfaces.

**Current Cursor Configuration** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "owasp-zap-security": {
      "url": "http://localhost:3000/sse",
      "env": {
        "ZAP_BASE_URL": "http://localhost:8080",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**VS Code Configuration** (`.vscode/mcp.json`):
```json
{
  "mcpServers": {
    "owasp-zap-security": {
      "url": "http://localhost:3000/sse",
      "env": {
        "ZAP_BASE_URL": "http://localhost:8080",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Available MCP Tools (Current)
The MCP server provides these 10 security scanning tools:
1. `zap_health_check` - Check ZAP service status
2. `zap_spider_scan` - Perform spider/crawl scans
3. `zap_active_scan` - Run active security scans
4. `zap_spider_status` - Check spider scan progress
5. `zap_active_scan_status` - Check active scan progress
6. `zap_get_alerts` - Retrieve security alerts
7. `zap_generate_html_report` - Generate HTML reports
8. `zap_generate_json_report` - Generate JSON reports
9. `zap_clear_session` - Clear ZAP session data
10. `zap_scan_summary` - Get scan summary information

### Legacy STDIO Mode (Fallback)
If SSE mode fails, fallback to STDIO mode (update container name):

```json
{
  "mcpServers": {
    "owasp-zap-security": {
      "command": "docker",
      "args": ["exec", "-i", "owasp-zap-mcp-image", "python", "-m", "owasp_zap_mcp.main"],
      "env": {
        "ZAP_BASE_URL": "http://zap:8080",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Troubleshooting & Fallback Strategies

### When MCP Tools Fail
If MCP tools fail (e.g., `zap_health_check` returns errors), follow this escalation path IMMEDIATELY:

1. **Quick ZAP Verification** (30 seconds max):
   ```bash
   # Check if ZAP is responding directly
   curl -s http://localhost:8080/JSON/core/view/version/
   ```
   If this returns `{"version":"X.X.X"}`, ZAP is working - proceed with direct API calls.

2. **Container Status Check**:
   ```bash
   docker-compose ps
   docker logs owasp-zap-mcp-image --tail 20  # For services profile
   docker logs owasp-zap-mcp-build --tail 20  # For build-dev profile
   ```
   Both `zap` and the MCP container should be running and healthy.

3. **MCP Server Health Check**:
   ```bash
   curl -s http://localhost:3000/health
   curl -s http://localhost:3000/status
   ```

4. **If ZAP responds but MCP doesn't**: Use direct ZAP API calls (see Fallback Commands below)

### Fallback Commands (Direct ZAP API)
When MCP is unresponsive but ZAP is working, use these direct API calls:

#### Complete Scan Workflow
```bash
# Set target URL
TARGET_URL="https://httpbin.org"

# Extract domain for directory structure
DOMAIN=$(echo "$TARGET_URL" | sed 's|https\?://||' | cut -d'/' -f1)
mkdir -p "reports/${DOMAIN}"

# Clear any previous session
curl -s "http://localhost:8080/JSON/core/action/newSession/" > /dev/null

# Start spider scan
echo "Starting spider scan for $TARGET_URL..."
SCAN_ID=$(curl -s "http://localhost:8080/JSON/spider/action/scan/?url=${TARGET_URL}&maxChildren=10&recurse=true" | jq -r '.scan')

# Wait for spider to complete
while true; do
    STATUS=$(curl -s "http://localhost:8080/JSON/spider/view/status/?scanId=${SCAN_ID}" | jq -r '.status')
    echo "Spider scan progress: ${STATUS}%"
    if [ "$STATUS" = "100" ]; then
        break
    fi
    sleep 5
done

# Start active scan
echo "Starting active security scan..."
ASCAN_ID=$(curl -s "http://localhost:8080/JSON/ascan/action/scan/?url=${TARGET_URL}&recurse=true" | jq -r '.scan')

# Monitor active scan (can generate reports while running)
echo "Active scan started with ID: $ASCAN_ID"
echo "Generating reports with current findings..."

# Generate all required reports
DOMAIN_UNDERSCORE=$(echo "$DOMAIN" | sed 's/\./_/g')

curl -s "http://localhost:8080/OTHER/core/other/htmlreport/" > "reports/${DOMAIN}/${DOMAIN_UNDERSCORE}_security_report.html"
curl -s "http://localhost:8080/OTHER/core/other/xmlreport/" > "reports/${DOMAIN}/${DOMAIN_UNDERSCORE}_security_report.xml"
curl -s "http://localhost:8080/OTHER/core/other/jsonreport/" > "reports/${DOMAIN}/${DOMAIN_UNDERSCORE}_security_report.json"
curl -s "http://localhost:8080/JSON/core/view/alerts/" > "reports/${DOMAIN}/${DOMAIN_UNDERSCORE}_alerts_summary.json"

# Generate scan summary
cat > "reports/${DOMAIN}/${DOMAIN_UNDERSCORE}_scan_summary.md" << EOF
# Security Scan Report for ${DOMAIN}

**Scan Date:** $(date)
**Target:** ${TARGET_URL}
**Scanner:** OWASP ZAP $(curl -s http://localhost:8080/JSON/core/view/version/ | jq -r '.version')

## Scan Status
- Spider Scan: ✅ Complete (100%)
- Active Scan: 🔄 In Progress
- Total Alerts: $(curl -s "http://localhost:8080/JSON/core/view/numberOfAlerts/" | jq -r '.numberOfAlerts')

## Report Files
1. ${DOMAIN_UNDERSCORE}_security_report.html - Detailed HTML report
2. ${DOMAIN_UNDERSCORE}_security_report.xml - XML format report
3. ${DOMAIN_UNDERSCORE}_security_report.json - JSON format report
4. ${DOMAIN_UNDERSCORE}_alerts_summary.json - Alerts data
5. ${DOMAIN_UNDERSCORE}_scan_summary.md - This summary

EOF

# Generate scan status
cat > "reports/${DOMAIN}/${DOMAIN_UNDERSCORE}_scan_status.md" << EOF
# Scan Status for ${DOMAIN}

**Last Updated:** $(date)
**Target:** ${TARGET_URL}

## Progress
- Spider Scan: ✅ Complete (100%)
- Active Scan: $(curl -s "http://localhost:8080/JSON/ascan/view/status/?scanId=${ASCAN_ID}" | jq -r '.status')%

## Statistics
- URLs Found: $(curl -s "http://localhost:8080/JSON/core/view/numberOfMessages/" | jq -r '.numberOfMessages')
- Alerts Generated: $(curl -s "http://localhost:8080/JSON/core/view/numberOfAlerts/" | jq -r '.numberOfAlerts')

EOF

echo "Reports generated in reports/${DOMAIN}/"
ls -la "reports/${DOMAIN}/"
```

### Decision Tree: MCP vs Direct API
- **Use MCP first**: Always try MCP tools initially
- **Switch to direct API if**: Health check fails OR any MCP command times out OR tool execution errors
- **Don't troubleshoot MCP**: If ZAP responds directly, just use the API
- **Time limit**: Don't spend more than 2 minutes on MCP troubleshooting

### Common Issues & Quick Fixes
- **MCP tool execution errors**: Tool registration issue - use direct API
- **SSE connection issues**: Check if port 3000 is accessible
- **Container networking**: Ensure docker-compose networking is working
- **Empty reports**: Ensure scans completed before generating reports
- **Permission errors**: Check Docker container permissions and volumes
- **ARM64 compatibility**: ZAP now uses `linux/amd64` platform for Apple Silicon

### Profile-Specific Troubleshooting

#### Services Profile Issues
```bash
# Check services profile containers
docker-compose --profile services ps
docker logs zap --tail 20
docker logs owasp-zap-mcp-image --tail 20
```

#### Development Profile Issues
```bash
# Check dev profile containers
docker-compose --profile dev ps
docker logs zap --tail 20
docker logs owasp-zap-mcp-dev --tail 20
```

#### Build Profile Issues
```bash
# Check build-dev profile containers
docker-compose --profile build-dev ps
docker logs zap --tail 20
docker logs owasp-zap-mcp-build --tail 20
```

### Example Directory Structure
```
reports/
├── httpbin.org/
│   ├── httpbin_org_security_report.html
│   ├── httpbin_org_security_report.xml
│   ├── httpbin_org_security_report.json
│   ├── httpbin_org_alerts_summary.json
│   ├── httpbin_org_scan_summary.md
│   └── httpbin_org_scan_status.md
├── example.com/
│   ├── example_com_security_report.html
│   ├── example_com_security_report.xml
│   ├── example_com_security_report.json
│   ├── example_com_alerts_summary.json
│   ├── example_com_scan_summary.md
│   └── example_com_scan_status.md
└── api.service.com/
    ├── api_service_com_security_report.html
    ├── api_service_com_security_report.xml
    ├── api_service_com_security_report.json
    ├── api_service_com_alerts_summary.json
    ├── api_service_com_scan_summary.md
    └── api_service_com_scan_status.md
```

## Best Practices

1. **Always follow directory structure**: Reports MUST go in `reports/{domain}/`
2. **Use consistent naming**: Replace dots with underscores in filenames
3. **Generate all report formats**: HTML, XML, JSON, and summary
4. **Include scan metadata**: Date, target, scanner version, status
5. **Monitor scan progress**: Don't wait for completion to generate initial reports
6. **Use fallback strategy**: Switch to direct API if MCP fails
7. **Document findings**: Include executive summary and recommendations
8. **Use appropriate profile**: Choose the right docker-compose profile for your use case
9. **Check container health**: Verify both ZAP and MCP containers are healthy before scanning
10. **Clear sessions**: Start with a clean ZAP session for each new target

## Quick Start Commands

### For Security Engineers
```bash
# Start services and perform scan
docker-compose --profile services up -d
curl -s http://localhost:3000/health  # Verify MCP health
curl -s http://localhost:8080/JSON/core/view/version/  # Verify ZAP health

# Use MCP tools or fallback to direct API if needed
```

### For Developers
```bash
# Local development
docker-compose --profile dev up -d
cd owasp_zap_mcp && pip install -e . && python -m owasp_zap_mcp.main --sse

# Container development
docker-compose --profile devcontainer up -d
docker exec -it owasp-zap-mcp-devcontainer bash

# Test builds
docker-compose --profile build-dev up -d
```
