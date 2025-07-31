# ADR-001: Strategic Approach to Deploying and Managing Haiven-based Model Context Protocol (MCP) Servers

## Status

**Approved** - Containerized Distribution Strategy adopted

## Decision Summary

We will adopt a **Containerized Distribution Strategy** for deploying and managing Haiven-based MCP servers, with Python as the primary implementation and Java as an enterprise alternative. This approach provides standardized deployment, security hardening, cross-platform compatibility, and enterprise-ready features while maintaining developer productivity and operational efficiency.

## Context

Following ADR-005(haiven) which established the decision to create an MCP server for AI tool integration, we now need to determine the optimal deployment, operational, and management strategy for these MCP server instances. The chosen approach will directly impact our ability to deliver reliable, secure, and scalable AI tool integrations.

### Current State
- Haiven API server is operational with API key authentication support
- Python MCP server implementation is complete with superior code quality
- Java MCP server exists as an alternative for enterprise users
- Manual setup currently required for end users

### Business Impact
- **Developer Experience**: Frictionless environment for building, testing, and iterating on MCP servers
- **Operational Efficiency**: Streamlined deployment, monitoring, and scaling across environments
- **Security Posture**: Proper authentication, authorization, and credential management
- **Scalability**: Accommodate growth in usage and demand with high availability
- **Integration**: Easy discoverability and consumption by diverse AI clients
- **Cost Management**: Optimize infrastructure and operational overhead

### Requirements
- **No Docker Compose dependency** - Simple `docker run` commands for end users
- **Environment variable configuration** - API keys and URLs configurable
- **Cross-platform compatibility** - Support for macOS, Windows, and Linux
- **Security hardening** - Non-root execution, isolated environments
- **Enterprise-ready** - Compliance, audit trails, and governance
- **AI tool integration** - Support for Claude Desktop, VS Code, Cursor

## Options Considered

### Option A: Containerized Distribution Strategy (Chosen)
**Description**: Standardize on containerized deployment using Docker with Python as primary implementation and Java as enterprise alternative.

**Consequences**:
- ✅ **Positive**: Consistent environment across all platforms and operating systems
- ✅ **Positive**: No runtime dependencies for end users (Python, Java, etc.)
- ✅ **Positive**: Easy updates via `docker pull thoughtworks/haiven-mcp-server`
- ✅ **Positive**: Isolated execution prevents conflicts with local development
- ✅ **Positive**: Version management through container tags and registries
- ✅ **Positive**: Standardized deployment across development, testing, and production
- ✅ **Positive**: Automated builds via CI/CD pipelines
- ✅ **Positive**: Health monitoring through container orchestration tools
- ✅ **Positive**: Resource isolation and predictable resource usage
- ✅ **Positive**: Rollback capabilities through container image versioning
- ✅ **Positive**: Isolated execution environment prevents system-level access
- ✅ **Positive**: Environment variable secrets management for API keys
- ✅ **Positive**: Non-root user execution for security
- ✅ **Positive**: Audit trail through container logs and monitoring
- ✅ **Positive**: Resource constraints through Docker limits
- ✅ **Positive**: Horizontal scaling via container orchestration
- ✅ **Positive**: Load balancing capabilities
- ✅ **Positive**: Performance monitoring through container metrics
- ✅ **Positive**: Standard container registry distribution
- ✅ **Positive**: Docker Hub integration for easy discovery
- ✅ **Positive**: GitHub Container Registry for version control integration
- ✅ **Positive**: CI/CD pipeline integration for automated releases
- ✅ **Positive**: Reduced support overhead through standardized deployment
- ✅ **Positive**: Lower infrastructure costs through efficient resource usage
- ✅ **Positive**: Reduced development time through consistent environments
- ✅ **Positive**: Automated testing reduces manual QA effort

- ❌ **Negative**: Docker knowledge required - Users must understand Docker basics
- ❌ **Negative**: Larger resource footprint - Containers require more memory/disk than binaries
- ❌ **Negative**: Network configuration complexity - Corporate proxies and firewalls
- ❌ **Negative**: Container privilege considerations - Security policies may block containers
- ❌ **Negative**: Container runtime dependency - Requires Docker or compatible runtime
- ❌ **Negative**: Platform-specific considerations - Windows, macOS, Linux differences
- ❌ **Negative**: Network access requirements - Must reach Haiven API endpoints
- ❌ **Negative**: Container registry access - Corporate networks may block registry access
- ❌ **Negative**: Container orchestration - More complex than simple binary execution
- ❌ **Negative**: Image management - Version control and cleanup
- ❌ **Negative**: Security scanning - Container vulnerability management
- ❌ **Negative**: Registry maintenance - Container registry costs and management

### Option B: Binary Distribution
**Description**: Distribute pre-compiled binaries for each target platform without containerization.

**Consequences**:
- ✅ **Positive**: No runtime dependencies - Direct execution
- ✅ **Positive**: Smaller file sizes - No container overhead
- ✅ **Positive**: Simple execution - No Docker knowledge required
- ✅ **Positive**: Lower resource usage - Minimal memory footprint

- ❌ **Negative**: Platform-specific builds required for each OS/architecture
- ❌ **Negative**: Complex distribution and version management
- ❌ **Negative**: Security vulnerabilities - No isolation from host system
- ❌ **Negative**: Difficult updates - Manual download and replacement
- ❌ **Negative**: No standardized deployment across environments
- ❌ **Negative**: Limited monitoring and health checks
- ❌ **Negative**: Complex dependency management
- ❌ **Negative**: Higher maintenance overhead for multiple platforms

### Option C: Package Manager Distribution
**Description**: Use platform-specific package managers (pip, npm, etc.) for distribution.

**Consequences**:
- ✅ **Positive**: Familiar to developers - Standard package management
- ✅ **Positive**: Automatic updates - Package manager handles updates
- ✅ **Positive**: Dependency resolution - Automatic dependency management

- ❌ **Negative**: Requires runtime dependencies - Python, Node.js, etc.
- ❌ **Negative**: More complex setup - Multiple package managers
- ❌ **Negative**: Platform-specific packaging - Different tools for each platform
- ❌ **Negative**: Security concerns - Direct access to system packages
- ❌ **Negative**: Version conflicts - Potential conflicts with existing packages
- ❌ **Negative**: Limited isolation - No container-level security

### Option D: Hybrid Approach
**Description**: Support multiple distribution methods (containers, binaries, packages) based on user preferences.

**Consequences**:
- ✅ **Positive**: Maximum flexibility - Users can choose preferred method
- ✅ **Positive**: Covers all use cases - Enterprise, development, edge cases

- ❌ **Negative**: High maintenance overhead - Multiple distribution pipelines
- ❌ **Negative**: Inconsistent user experience - Different setup for different methods
- ❌ **Negative**: Complex testing - Need to test all distribution methods
- ❌ **Negative**: Higher development costs - Multiple implementation paths
- ❌ **Negative**: Confusing documentation - Multiple setup guides
- ❌ **Negative**: Support complexity - Multiple troubleshooting paths

### Option E: Do Nothing
**Description**: Continue with current manual setup approach without standardized distribution.

**Consequences**:
- ✅ **Positive**: No immediate development effort required
- ✅ **Positive**: No new dependencies or infrastructure needed

- ❌ **Negative**: Poor developer experience - Manual setup for each user
- ❌ **Negative**: Inconsistent deployments - Different setups across environments
- ❌ **Negative**: Security risks - No standardized security practices
- ❌ **Negative**: Limited scalability - Manual deployment doesn't scale
- ❌ **Negative**: Poor user adoption - Friction in getting started
- ❌ **Negative**: No enterprise features - Missing compliance and governance
- ❌ **Negative**: Difficult troubleshooting - No standardized environment

## Decision

We will adopt **Option A: Containerized Distribution Strategy** with the following implementation details:

### Technology Choice: Python Implementation
- **Rationale**: Superior code quality, maintainability, testing, and documentation
- **Architecture**: Clean modular design with proper abstractions
- **Dependencies**: Minimal (4 main deps vs 10+ framework deps)
- **Performance**: Faster startup, smaller container size
- **Decision**: Chosen as primary implementation with Java as enterprise alternative

### Containerization Approach
1. **Python MCP Server**: Containerized with optimized Dockerfile
2. **Configuration**: Environment variables for API keys and URLs
3. **Distribution**: Container registry (Docker Hub, GitHub Container Registry)
4. **Java Implementation**: Maintained as alternative for enterprise users requiring Java

### User Experience
```bash
# Simple run command
docker run -i --rm \
  -e HAIVEN_API_KEY="your-api-key" \
  -e HAIVEN_API_URL="http://host.docker.internal:8080" \
  thoughtworks/haiven-mcp-server
```

### AI Tool Integration
```json
{
  "mcpServers": {
    "haiven": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "HAIVEN_API_KEY=your-key",
        "-e", "HAIVEN_API_URL=http://host.docker.internal:8080",
        "thoughtworks/haiven-mcp-server"
      ]
    }
  }
}
```

## Technical Specifications

### Environment Variables
- `HAIVEN_API_KEY`: API key for authentication
- `HAIVEN_API_URL`: Base URL of Haiven API (e.g., `http://localhost:8080` for local development)
- `HAIVEN_DISABLE_AUTH`: Disable authentication (development only)

**Note**: MCP servers communicate via stdin/stdout, not HTTP ports. The `HAIVEN_API_URL` points to your actual Haiven API server, not the MCP server itself.

**Important**: When running in Docker, use `host.docker.internal` to access your host machine's Haiven API. This works cross-platform on macOS, Windows, and Linux.

### Configuration Examples

#### Basic Usage
```bash
docker run -i --rm \
  -e HAIVEN_API_KEY="your-api-key" \
  -e HAIVEN_API_URL="http://host.docker.internal:8080" \
  ghcr.io/tw-haiven/haiven-mcp-server
```

## CPU Architecture Compatibility

### Multi-Architecture Support
The containerized approach will support multiple CPU architectures:
- **linux/amd64**: Intel/AMD 64-bit processors (most common)
- **linux/arm64**: ARM 64-bit processors (Apple Silicon, ARM servers)
- **linux/arm/v7**: ARM 32-bit processors (Raspberry Pi, older ARM devices)

### Implementation Strategy
```bash
# Create and use a new builder instance with multi-architecture support
docker buildx create --name multiarch --driver docker-container --use

# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t ghcr.io/tw-haiven/haiven-mcp-server:latest \
  --push .
```

### User Experience Impact
- **Automatic architecture detection**: Docker will pull the correct architecture
- **Transparent to users**: No manual architecture selection required
- **Wider compatibility**: Works on Intel, AMD, and ARM processors
- **Cloud deployment ready**: Compatible with most cloud providers

## Risk Mitigation

### Technical Risks
- **Container runtime dependency**: Provide alternative binary distribution for edge cases
- **Network connectivity**: Document proxy configuration and firewall requirements
- **Security policies**: Work with enterprise security teams for container approval
- **CPU architecture compatibility**: Implement multi-architecture builds to support x86_64, ARM64, and ARM32
- **Architecture-specific dependencies**: Test Python packages for compatibility across different CPU architectures

### Operational Risks
- **Container registry availability**: Use multiple registry providers
- **Image size optimization**: Implement multi-stage builds and layer optimization
- **Version management**: Implement semantic versioning and automated tagging

### User Experience Risks
- **Docker knowledge requirement**: Provide comprehensive documentation and examples
- **Configuration complexity**: Create configuration generators and templates
- **Platform differences**: Test on multiple operating systems and architectures

## Success Metrics

### Adoption Metrics
- Number of container downloads from registry
- User feedback and satisfaction scores
- Time to first successful deployment

### Performance Metrics
- Container startup time (< 5 seconds)
- Memory usage (< 200MB per container)
- Network latency to Haiven API

### Operational Metrics
- Container build success rate (> 99%)
- Security scan pass rate (100%)
- Documentation completeness score

## Stakeholders to Consult

- **Development Team**: For implementation and testing
- **DevOps/Platform Team**: For CI/CD pipeline setup
- **Security Team**: For container security review and approval
- **Enterprise Architecture**: For compliance and governance requirements
- **Product Management**: For user experience and adoption strategy
- **Customer Success**: For user onboarding and support documentation
