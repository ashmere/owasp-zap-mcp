# OWASP ZAP MCP Server Threat Model

**Author**: Mat Davies ([@ashmere](https://github.com/ashmere/))  
**Project**: [owasp-zap-mcp](https://github.com/ashmere/owasp-zap-mcp)  
**Date**: May 2025  
**Methodology**: STRIDE/DREAD Analysis

## Executive Summary

This document presents a comprehensive threat model for the OWASP ZAP Model Context Protocol (MCP) Server, a system designed to integrate OWASP ZAP security scanning capabilities with AI-powered development environments. The analysis uses STRIDE methodology for threat categorization and DREAD methodology for risk assessment, with impact scaling adjusted for local development tool usage.

**Key Findings:**

- The system presents a **moderate overall risk profile** appropriate for local development tools
- Primary concerns center around **container security**, **network exposure**, and **scan target manipulation**
- Risk is significantly mitigated by the **local development context** and **trusted environment assumptions**
- Most threats have **low to moderate impact** due to limited scope and single-user deployment

## Scope and Boundaries

### In Scope

This threat model covers the following components and interactions:

1. **AI Development Environment** (Cursor IDE, VS Code with MCP clients)
2. **MCP Server Container** (owasp-zap-mcp running on port 3000)
3. **OWASP ZAP Container** (ZAP scanner running on port 8080)
4. **Docker Network Communication** (container-to-container)
5. **Host System Integration** (port exposure, file system access)
6. **External Scan Targets** (websites and applications being scanned)
7. **Communication Protocols** (HTTP/SSE, MCP protocol, ZAP REST API)

### Out of Scope

The following elements are explicitly excluded from this threat model:

1. **AI Model Security**: Per requirements, we trust the AI models themselves and do not analyze threats related to AI model manipulation, prompt injection, or model behavior
2. **Host Operating System**: We assume the developer's local machine is trusted and secure
3. **IDE Security**: We trust the development environment (Cursor, VS Code) as secure
4. **Docker Engine Security**: We assume Docker itself is properly configured and secure
5. **Network Infrastructure**: We assume the local network environment is trusted
6. **Physical Security**: Physical access to the developer's machine is out of scope

### Assumptions

**Critical Trust Assumptions:**

- **AI Models are Trusted**: We assume AI models (Claude, GPT, etc.) are benign and will not attempt malicious actions
- **Local Development Environment is Trusted**: The developer's machine, IDE, and local network are assumed secure
- **Developer Intent is Benign**: The developer using this tool has legitimate security testing purposes
- **Scan Targets are Authorized**: The developer has permission to scan the target applications

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRUSTED ZONE                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   Cursor IDE    │    │   Developer     │                    │
│  │                 │    │   Host System   │                    │
│  │ - MCP Client    │    │                 │                    │
│  │ - AI Assistant  │    │ - Docker Engine │                    │
│  │ - Code Analysis │    │ - File System   │                    │
│  └─────────────────┘    └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTP/SSE (localhost:3000)
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SEMI-TRUSTED ZONE                              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                Docker Network (zap-network)                 │ │
│  │                                                             │ │
│  │  ┌─────────────────┐    ┌─────────────────┐                │ │
│  │  │ MCP Server      │    │ OWASP ZAP       │                │ │
│  │  │                 │◄──►│                 │                │ │
│  │  │ - FastAPI       │    │ - REST API      │                │ │
│  │  │ - SSE Handler   │    │ - Scanner       │                │ │
│  │  │ - Tool Registry │    │ - Proxy Engine  │                │ │
│  │  │ Port: 3000      │    │ Port: 8080      │                │ │
│  │  └─────────────────┘    └─────────────────┘                │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTP/HTTPS
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                   UNTRUSTED ZONE                                │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ External Web    │    │ Target          │                    │
│  │ Applications    │    │ Applications    │                    │
│  │                 │    │                 │                    │
│  │ - Scan Targets  │    │ - APIs          │                    │
│  │ - Potentially   │    │ - Web Services  │                    │
│  │   Malicious     │    │                 │                    │
│  └─────────────────┘    └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

## Trust Zones and Boundaries

### Trust Zone Definitions

1. **Trusted Zone** (Developer Environment)
   - Developer's local machine
   - IDE and development tools
   - Local file system
   - **Trust Level**: High - Assumed secure and benign

2. **Semi-Trusted Zone** (Containerized Services)
   - MCP Server container
   - ZAP Scanner container
   - Docker network
   - **Trust Level**: Medium - Isolated but potentially vulnerable

3. **Untrusted Zone** (External Targets)
   - Websites and applications being scanned
   - External network resources
   - **Trust Level**: Low - Potentially malicious

### Trust Boundaries

1. **Boundary A**: Host System ↔ Docker Containers
   - **Crossing**: Port exposure (3000, 8080), volume mounts, Docker socket
   - **Controls**: Container isolation, port binding restrictions, volume permissions

2. **Boundary B**: MCP Server ↔ ZAP Scanner
   - **Crossing**: HTTP API calls within Docker network
   - **Controls**: Network isolation, API authentication (disabled), input validation

3. **Boundary C**: ZAP Scanner ↔ External Targets
   - **Crossing**: HTTP/HTTPS requests to scan targets
   - **Controls**: ZAP's built-in protections, scan scope limitations

## Threat Analysis (STRIDE)

### Impact Scaling for Local Development Tools

**Adjusted DREAD Scoring (1-5 scale):**

- **Damage Potential**: Reduced by 1-2 points (local vs enterprise impact)
- **Reproducibility**: No adjustment (technical factors unchanged)
- **Exploitability**: No adjustment (technical difficulty unchanged)  
- **Affected Users**: Reduced by 2-3 points (single developer vs many users)
- **Discoverability**: Reduced by 1 point (limited exposure vs internet-facing)

**Risk Levels:**

- **Critical (20-25)**: Immediate action required
- **High (15-19)**: Address within sprint
- **Medium (10-14)**: Address within release cycle
- **Low (5-9)**: Address when convenient
- **Minimal (1-4)**: Monitor only

---

### S - Spoofing Threats

#### S1: MCP Client Impersonation

**Description**: Malicious process impersonates legitimate MCP client to access ZAP functionality.

**Attack Vectors**:

- Rogue process connects to SSE endpoint (localhost:3000)
- Malicious browser tab accesses MCP server
- Process hijacking of legitimate MCP session

**DREAD Assessment**:

- Damage: 2 (Limited to local scan capabilities)
- Reproducibility: 4 (Easy to reproduce)
- Exploitability: 3 (Requires local access)
- Affected Users: 1 (Single developer)
- Discoverability: 2 (Localhost ports discoverable)
- **Total: 12 (Medium)**

**Current Mitigations**:

- Localhost-only binding
- No authentication required (by design)
- Container isolation

**Recommended Mitigations**:

- Implement session tokens for MCP connections
- Add origin validation for SSE connections
- Monitor for unexpected connection patterns

#### S2: ZAP API Impersonation

**Description**: Malicious process impersonates MCP server to access ZAP API directly.

**Attack Vectors**:

- Direct API calls to ZAP container (localhost:8080)
- Container-to-container API access
- API key bypass (currently disabled)

**DREAD Assessment**:

- Damage: 3 (Full ZAP functionality access)
- Reproducibility: 4 (Easy to reproduce)
- Exploitability: 2 (Requires container network access)
- Affected Users: 1 (Single developer)
- Discoverability: 3 (API endpoints well-documented)
- **Total: 13 (Medium)**

**Current Mitigations**:

- API key disabled (internal network only)
- Container network isolation
- Localhost-only exposure

**Recommended Mitigations**:

- Enable API key authentication for production use
- Implement request rate limiting
- Add API access logging

---

### T - Tampering Threats

#### T1: Scan Report Manipulation

**Description**: Malicious actor modifies scan reports to hide vulnerabilities or inject false positives.

**Attack Vectors**:

- File system access to reports directory
- Manipulation during report generation
- Container volume mount exploitation

**DREAD Assessment**:

- Damage: 3 (False security assessment)
- Reproducibility: 3 (Requires file system access)
- Exploitability: 2 (Requires local access)
- Affected Users: 1 (Single developer)
- Discoverability: 2 (Report locations predictable)
- **Total: 11 (Medium)**

**Current Mitigations**:

- Container isolation
- File system permissions
- Organized directory structure

**Recommended Mitigations**:

- Implement report integrity checksums
- Add report generation logging
- Use read-only volume mounts where possible

#### T2: MCP Message Tampering

**Description**: Modification of MCP protocol messages between client and server.

**Attack Vectors**:

- Man-in-the-middle on localhost connections
- Process memory manipulation
- SSE stream injection

**DREAD Assessment**:

- Damage: 2 (Limited to scan parameters)
- Reproducibility: 2 (Requires sophisticated attack)
- Exploitability: 4 (Localhost traffic easier to intercept)
- Affected Users: 1 (Single developer)
- Discoverability: 1 (Requires protocol knowledge)
- **Total: 10 (Medium)**

**Current Mitigations**:

- Localhost-only communication
- JSON schema validation
- Container isolation

**Recommended Mitigations**:

- Implement message signing
- Add request/response logging
- Use TLS for localhost connections

#### T3: Container Configuration Tampering

**Description**: Modification of Docker container configurations or environment variables.

**Attack Vectors**:

- Docker socket access
- Environment variable manipulation
- Container restart with modified parameters

**DREAD Assessment**:

- Damage: 4 (Full system compromise)
- Reproducibility: 3 (Requires Docker access)
- Exploitability: 2 (Requires elevated privileges)
- Affected Users: 1 (Single developer)
- Discoverability: 2 (Docker commands well-known)
- **Total: 12 (Medium)**

**Current Mitigations**:

- Container isolation
- Non-root user in containers
- Limited volume mounts

**Recommended Mitigations**:

- Implement container image signing
- Add configuration monitoring
- Use Docker secrets for sensitive data

---

### R - Repudiation Threats

#### R1: Scan Activity Denial

**Description**: Developer denies performing security scans that may have caused issues.

**Attack Vectors**:

- Lack of audit logging
- Anonymous scan execution
- Log tampering or deletion

**DREAD Assessment**:

- Damage: 2 (Accountability issues)
- Reproducibility: 4 (Easy to reproduce)
- Exploitability: 3 (Requires log access)
- Affected Users: 1 (Single developer)
- Discoverability: 3 (Log locations predictable)
- **Total: 13 (Medium)**

**Current Mitigations**:

- Container logging
- ZAP built-in logging
- Docker log retention

**Recommended Mitigations**:

- Implement comprehensive audit logging
- Add user identification to logs
- Use centralized log collection
- Implement log integrity protection

#### R2: Report Generation Denial

**Description**: Denial of generating or modifying security reports.

**Attack Vectors**:

- Report timestamp manipulation
- File system timestamp changes
- Report content modification without traces

**DREAD Assessment**:

- Damage: 2 (Evidence integrity)
- Reproducibility: 3 (Requires file system access)
- Exploitability: 2 (Requires local access)
- Affected Users: 1 (Single developer)
- Discoverability: 2 (File system access patterns)
- **Total: 10 (Medium)**

**Current Mitigations**:

- File system timestamps
- Container isolation
- Organized report structure

**Recommended Mitigations**:

- Implement report digital signatures
- Add report generation audit trail
- Use immutable storage for reports

---

### I - Information Disclosure Threats

#### I1: Scan Target Information Leakage

**Description**: Sensitive information about scan targets exposed through logs, reports, or network traffic.

**Attack Vectors**:

- Log file access
- Report file access
- Network traffic interception
- Container memory dumps

**DREAD Assessment**:

- Damage: 3 (Sensitive target information)
- Reproducibility: 4 (Easy to reproduce)
- Exploitability: 2 (Requires local access)
- Affected Users: 1 (Single developer)
- Discoverability: 3 (Log and report locations known)
- **Total: 13 (Medium)**

**Current Mitigations**:

- Container isolation
- Localhost-only communication
- File system permissions

**Recommended Mitigations**:

- Implement log sanitization
- Add data classification to reports
- Use encrypted storage for sensitive data
- Implement log rotation and cleanup

#### I2: ZAP Configuration Exposure

**Description**: ZAP configuration details exposed, revealing security testing capabilities and limitations.

**Attack Vectors**:

- Configuration file access
- API endpoint enumeration
- Container environment variable exposure

**DREAD Assessment**:

- Damage: 2 (Tool capability disclosure)
- Reproducibility: 3 (Requires container access)
- Exploitability: 2 (Requires local access)
- Affected Users: 1 (Single developer)
- Discoverability: 3 (Standard ZAP configuration)
- **Total: 11 (Medium)**

**Current Mitigations**:

- Container isolation
- No external network exposure
- Standard ZAP configuration

**Recommended Mitigations**:

- Implement configuration encryption
- Add access controls to configuration
- Use environment-specific configurations

#### I3: MCP Protocol Information Leakage

**Description**: MCP protocol details and tool capabilities exposed to unauthorized parties.

**Attack Vectors**:

- SSE endpoint enumeration
- Tool discovery API access
- Protocol message interception

**DREAD Assessment**:

- Damage: 1 (Tool capability disclosure)
- Reproducibility: 4 (Easy to reproduce)
- Exploitability: 3 (Requires network access)
- Affected Users: 1 (Single developer)
- Discoverability: 4 (Standard MCP protocol)
- **Total: 13 (Medium)**

**Current Mitigations**:

- Localhost-only binding
- Standard MCP protocol
- No sensitive data in protocol

**Recommended Mitigations**:

- Implement protocol encryption
- Add authentication to tool discovery
- Use capability-based access control

---

### D - Denial of Service Threats

#### D1: Resource Exhaustion via Scan Overload

**Description**: Excessive or malicious scan requests overwhelm ZAP or MCP server resources.

**Attack Vectors**:

- Rapid scan initiation
- Large-scale spider scans
- Memory exhaustion attacks
- CPU exhaustion via complex scans

**DREAD Assessment**:

- Damage: 3 (Service unavailability)
- Reproducibility: 4 (Easy to reproduce)
- Exploitability: 3 (Requires API access)
- Affected Users: 1 (Single developer)
- Discoverability: 3 (Resource limits discoverable)
- **Total: 14 (Medium)**

**Current Mitigations**:

- Container resource limits
- ZAP built-in protections
- Single-user deployment

**Recommended Mitigations**:

- Implement scan rate limiting
- Add resource monitoring and alerting
- Implement scan queue management
- Add scan timeout controls

#### D2: Port Exhaustion Attack

**Description**: Exhaustion of available ports on localhost, preventing legitimate connections.

**Attack Vectors**:

- Rapid connection establishment
- Connection pool exhaustion
- Socket resource exhaustion

**DREAD Assessment**:

- Damage: 2 (Service unavailability)
- Reproducibility: 3 (Requires sustained attack)
- Exploitability: 3 (Requires local access)
- Affected Users: 1 (Single developer)
- Discoverability: 2 (Requires network knowledge)
- **Total: 11 (Medium)**

**Current Mitigations**:

- Operating system limits
- Container isolation
- Connection pooling

**Recommended Mitigations**:

- Implement connection rate limiting
- Add connection monitoring
- Use connection pool management

#### D3: Log Storage Exhaustion

**Description**: Excessive logging fills available disk space, causing system failure.

**Attack Vectors**:

- Verbose logging attacks
- Log rotation bypass
- Disk space exhaustion

**DREAD Assessment**:

- Damage: 3 (System unavailability)
- Reproducibility: 3 (Requires sustained activity)
- Exploitability: 2 (Requires log generation capability)
- Affected Users: 1 (Single developer)
- Discoverability: 2 (Log locations predictable)
- **Total: 11 (Medium)**

**Current Mitigations**:

- Container storage limits
- Docker log rotation
- File system monitoring

**Recommended Mitigations**:

- Implement log size limits
- Add disk space monitoring
- Use log compression and archival

---

### E - Elevation of Privilege Threats

#### E1: Container Escape

**Description**: Escape from container isolation to gain host system access.

**Attack Vectors**:

- Docker vulnerability exploitation
- Privileged container abuse
- Volume mount exploitation
- Kernel vulnerability exploitation

**DREAD Assessment**:

- Damage: 5 (Full host compromise)
- Reproducibility: 2 (Requires specific vulnerabilities)
- Exploitability: 2 (Requires advanced techniques)
- Affected Users: 1 (Single developer)
- Discoverability: 1 (Requires deep technical knowledge)
- **Total: 11 (Medium)**

**Current Mitigations**:

- Non-root container users
- Limited volume mounts
- Container isolation
- No privileged containers

**Recommended Mitigations**:

- Implement container security scanning
- Use minimal base images
- Add runtime security monitoring
- Implement AppArmor/SELinux policies

#### E2: Docker Socket Abuse

**Description**: Abuse of Docker socket access to gain elevated privileges.

**Attack Vectors**:

- Docker socket mounting
- Container management API abuse
- Host container creation

**DREAD Assessment**:

- Damage: 5 (Full host compromise)
- Reproducibility: 3 (Requires socket access)
- Exploitability: 2 (Requires Docker knowledge)
- Affected Users: 1 (Single developer)
- Discoverability: 2 (Socket mounting visible)
- **Total: 13 (Medium)**

**Current Mitigations**:

- Limited Docker socket exposure
- DevContainer-only socket mounting
- Container isolation

**Recommended Mitigations**:

- Avoid Docker socket mounting
- Use Docker-in-Docker alternatives
- Implement socket access controls
- Add Docker API monitoring

#### E3: ZAP Privilege Escalation

**Description**: Exploitation of ZAP vulnerabilities to gain elevated privileges within container.

**Attack Vectors**:

- ZAP software vulnerabilities
- Java runtime exploitation
- Plugin vulnerability exploitation

**DREAD Assessment**:

- Damage: 3 (Container compromise)
- Reproducibility: 2 (Requires specific vulnerabilities)
- Exploitability: 3 (Requires ZAP knowledge)
- Affected Users: 1 (Single developer)
- Discoverability: 2 (ZAP vulnerabilities published)
- **Total: 11 (Medium)**

**Current Mitigations**:

- Latest ZAP stable image
- Non-root container user
- Container isolation

**Recommended Mitigations**:

- Implement regular image updates
- Add vulnerability scanning
- Use minimal ZAP configuration
- Implement runtime monitoring

---

## Risk Summary Matrix

| Threat ID | Category | Threat | Risk Level | Priority |
|-----------|----------|---------|------------|----------|
| S1 | Spoofing | MCP Client Impersonation | Medium (12) | 3 |
| S2 | Spoofing | ZAP API Impersonation | Medium (13) | 3 |
| T1 | Tampering | Scan Report Manipulation | Medium (11) | 3 |
| T2 | Tampering | MCP Message Tampering | Medium (10) | 4 |
| T3 | Tampering | Container Configuration Tampering | Medium (12) | 3 |
| R1 | Repudiation | Scan Activity Denial | Medium (13) | 3 |
| R2 | Repudiation | Report Generation Denial | Medium (10) | 4 |
| I1 | Information Disclosure | Scan Target Information Leakage | Medium (13) | 3 |
| I2 | Information Disclosure | ZAP Configuration Exposure | Medium (11) | 3 |
| I3 | Information Disclosure | MCP Protocol Information Leakage | Medium (13) | 3 |
| D1 | Denial of Service | Resource Exhaustion via Scan Overload | Medium (14) | 2 |
| D2 | Denial of Service | Port Exhaustion Attack | Medium (11) | 3 |
| D3 | Denial of Service | Log Storage Exhaustion | Medium (11) | 3 |
| E1 | Elevation of Privilege | Container Escape | Medium (11) | 3 |
| E2 | Elevation of Privilege | Docker Socket Abuse | Medium (13) | 3 |
| E3 | Elevation of Privilege | ZAP Privilege Escalation | Medium (11) | 3 |

**Overall Risk Assessment**: **MEDIUM**

All identified threats fall within the Medium risk category (10-14 points), which is appropriate for a local development tool. No Critical or High-risk threats were identified due to the limited scope, single-user deployment, and trusted environment assumptions.

## Mitigation Strategies

### Immediate Actions (Priority 1-2)

1. **Resource Management** (D1)
   - Implement scan rate limiting
   - Add resource monitoring
   - Configure container resource limits

2. **Access Controls** (S1, S2, E2)
   - Implement MCP session tokens
   - Enable ZAP API key authentication for production
   - Restrict Docker socket access

### Short-term Actions (Priority 3)

1. **Logging and Monitoring**
   - Implement comprehensive audit logging
   - Add security event monitoring
   - Implement log integrity protection

2. **Data Protection**
   - Implement report integrity checksums
   - Add data classification to reports
   - Use encrypted storage for sensitive data

3. **Container Security**
   - Implement container security scanning
   - Add runtime security monitoring
   - Use minimal base images

### Long-term Actions (Priority 4)

1. **Protocol Security**
   - Implement MCP message signing
   - Add TLS for localhost connections
   - Use capability-based access control

2. **Advanced Monitoring**
   - Implement behavioral analysis
   - Add anomaly detection
   - Use centralized log collection

## Monitoring and Detection

### Key Security Metrics

1. **Connection Monitoring**
   - Unexpected MCP connections
   - Unusual API access patterns
   - Failed authentication attempts

2. **Resource Monitoring**
   - CPU and memory usage spikes
   - Disk space consumption
   - Network traffic anomalies

3. **Scan Monitoring**
   - Scan frequency and duration
   - Target diversity and patterns
   - Error rates and failures

### Recommended Monitoring Tools

1. **Container Monitoring**
   - Docker stats and logs
   - Container resource monitoring
   - Security event logging

2. **Network Monitoring**
   - Port usage monitoring
   - Connection tracking
   - Traffic analysis

3. **File System Monitoring**
   - Report generation tracking
   - Configuration change detection
   - Log file monitoring

## Conclusion

The OWASP ZAP MCP Server presents a **moderate risk profile** appropriate for its intended use as a local development security tool. The threat analysis identified 16 potential threats across all STRIDE categories, with all threats falling within the Medium risk range (10-14 points) when adjusted for local development context.

### Key Findings

1. **No Critical Threats**: The local development context and trusted environment assumptions significantly reduce the impact of potential threats.

2. **Balanced Risk Distribution**: Threats are evenly distributed across STRIDE categories, with no single category dominating the risk landscape.

3. **Manageable Risk Level**: All identified risks can be effectively mitigated through standard security practices and reasonable development effort.

4. **Context-Appropriate Security**: The security posture aligns well with the tool's intended use case and deployment environment.

### Recommendations

1. **Implement Priority 1-2 mitigations** to address the highest-impact threats
2. **Establish monitoring and logging** to detect potential security events
3. **Regular security reviews** as the system evolves and new features are added
4. **Consider threat model updates** if deployment context changes (e.g., multi-user, production use)

The threat model should be reviewed and updated annually or when significant changes are made to the system architecture, deployment model, or threat landscape.
