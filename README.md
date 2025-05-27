# OWASP ZAP Domain Scanner

Automated security scanning tool that organizes reports by domain in a structured directory format.

## Features

- 🕷️ **Spider Scanning**: Automatically discovers URLs on target domains
- 🔍 **Active Security Scanning**: Comprehensive vulnerability testing
- 📁 **Organized Reports**: Automatically creates `reports/<domain>/` directory structure
- 📊 **Multiple Report Formats**: Markdown, JSON, and HTML reports
- 🎯 **Domain-based Organization**: Clean separation of scan results by domain

## Directory Structure

```
reports/
└── <domain>/
    ├── security_report.md      # Detailed markdown report
    ├── security_summary.json   # Machine-readable summary
    └── security_report.html    # Visual HTML report
```

## Prerequisites

1. **OWASP ZAP**: Must be running and accessible
   ```bash
   # Using Docker (recommended)
   docker run -d -p 8080:8080 --name zap zaproxy/zap-stable \
     zap.sh -daemon -host 0.0.0.0 -port 8080 \
     -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true
   ```

2. **Python 3** with requests module:
   ```bash
   pip3 install requests
   ```

## Usage

### Quick Start
```bash
# Scan a domain (easiest method)
./scan.sh https://example.com

# Scan with custom options
./scan.sh https://example.com --max-children 20
```

### Advanced Usage
```bash
# Direct Python script usage
python3 scan_domain.py https://example.com

# Custom ZAP instance
python3 scan_domain.py https://example.com --zap-host 192.168.1.100 --zap-port 8090

# Limit spider depth
python3 scan_domain.py https://example.com --max-children 5
```

## Command Line Options

- `url`: Target URL to scan (required)
- `--zap-host`: ZAP host address (default: localhost)
- `--zap-port`: ZAP port number (default: 8080)
- `--max-children`: Maximum spider children per URL (default: 10)

## Example Output

```
🎯 Scanning domain: example.com
🔗 Target URL: https://example.com
📁 Reports will be saved to: reports/example.com
✅ ZAP is running (version 2.16.1)
✅ New ZAP session started
🕷️ Starting spider scan on https://example.com
Spider scan progress: 100%
✅ Spider scan completed
🔍 Starting active security scan on https://example.com
📊 Collecting scan results...
📈 Scan Results:
   - Total alerts: 45
   - URLs discovered: 12
   - High risk: 0
   - Medium risk: 8
   - Low risk: 25
   - Informational: 12
📝 Generating reports...
✅ Markdown report: reports/example.com/security_report.md
✅ JSON summary: reports/example.com/security_summary.json
✅ HTML report: reports/example.com/security_report.html

🎉 Scan completed! Reports saved to: reports/example.com
```

## Report Types

### 1. Markdown Report (`security_report.md`)
- Executive summary with key metrics
- Detailed vulnerability descriptions
- Risk categorization and recommendations
- Complete technical analysis

### 2. JSON Summary (`security_summary.json`)
- Machine-readable format
- Scan metadata and statistics
- Top security issues
- Structured recommendations
- Perfect for automation and integration

### 3. HTML Report (`security_report.html`)
- Visual report with charts and graphs
- Complete ZAP-generated analysis
- Suitable for stakeholder presentations
- Interactive vulnerability details

## Integration Examples

### CI/CD Pipeline
```bash
# In your CI/CD script
./scan.sh https://staging.example.com
if [ $? -eq 0 ]; then
    echo "Security scan completed successfully"
    # Process reports/example.com/ directory
else
    echo "Security scan failed"
    exit 1
fi
```

### Automated Monitoring
```bash
# Cron job for regular scanning
0 2 * * 0 /path/to/scan.sh https://production.example.com
```

## Troubleshooting

### ZAP Not Running
```bash
# Check if ZAP is accessible
curl http://localhost:8080/JSON/core/view/version/

# Start ZAP with Docker
docker run -d -p 8080:8080 zaproxy/zap-stable zap.sh -daemon -host 0.0.0.0 -port 8080
```

### Permission Issues
```bash
# Make scripts executable
chmod +x scan.sh scan_domain.py
```

### Missing Dependencies
```bash
# Install Python requests
pip3 install requests

# Or using system package manager
sudo apt-get install python3-requests  # Ubuntu/Debian
sudo yum install python3-requests      # CentOS/RHEL
```

## Security Considerations

- **Network Access**: Ensure ZAP can reach target domains
- **Rate Limiting**: Some sites may block aggressive scanning
- **Legal Compliance**: Only scan domains you own or have permission to test
- **Resource Usage**: Active scans can be resource-intensive

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.