# Build Strategies for Haiven MCP Server

This document explains the dual build strategy implemented for the Haiven MCP Server, providing both multi-architecture support and security-focused builds.

## Overview

The build system implements a single, optimized approach:

1. **Buildx (Multi-Architecture)**: Modern Docker approach for cross-platform compatibility with comprehensive testing

## Build Strategy

### Docker Buildx (Multi-Architecture)

**Purpose**: Multi-architecture support for cross-platform distribution

**Features**:
- ✅ **Multi-architecture support**: AMD64 and ARM64
- ✅ **Cross-platform compatibility**: macOS, Windows, Linux
- ✅ **Modern Docker approach**: Uses `docker buildx`
- ✅ **Caching optimization**: GitHub Actions cache integration
- ✅ **Comprehensive testing**: Architecture-specific validation
- ✅ **Security scanning**: Integrated Semgrep scanning
- ✅ **Pre-commit checks**: Code quality enforcement

**Use Cases**:
- Production distribution
- Cross-platform deployment
- End-user installations
- Cloud deployments
- Enterprise deployments

**Build Command**:
```bash
# Local build
./scripts/build_multiarch.sh

# CI/CD (GitHub Actions)
# Automatically triggered on push/PR
```

## Security Integration

### Semgrep Scanning

Both build strategies include comprehensive security scanning:

- **Daily scheduled scans**: Automatic security checks
- **High severity blocking**: Fails on critical security issues
- **SARIF reporting**: Integration with GitHub Security
- **Artifact retention**: 7-day retention for analysis

### Pre-commit Checks

Code quality is enforced through pre-commit hooks:

- **Python formatting**: Black + Ruff
- **Type checking**: MyPy integration
- **Import sorting**: isort with Black profile
- **YAML validation**: yamllint for configuration files
- **Docker linting**: hadolint for Dockerfile validation
- **Commit standards**: Conventional commit format

## Comparison with Main Haiven Repository

| Feature | Haiven Main | MCP Server |
|---------|-------------|------------|
| **Build Tool** | Kaniko | Buildx |
| **Multi-Arch** | ❌ Single | ✅ Multi-Arch |
| **Security** | ✅ Semgrep | ✅ Semgrep |
| **Pre-commit** | ✅ Yes | ✅ Yes |
| **Testing** | ✅ Comprehensive | ✅ Container-focused |
| **Distribution** | ✅ Registry push | ✅ Registry push |

## Architecture Support

### Buildx Approach
- **AMD64**: Intel/AMD processors
- **ARM64**: Apple Silicon, ARM servers
- **Future**: ARM32 support planned

### Buildx Approach (Current)
- **AMD64**: Intel/AMD processors
- **ARM64**: Apple Silicon, ARM servers
- **Future**: ARM32 support planned

## Testing Strategy

### Multi-Architecture Testing (Buildx)
```bash
# Test both architectures
./scripts/test_multiarch.sh

# Test specific architecture
docker run --rm --platform linux/amd64 image:tag python -c "import sys; print('test')"
docker run --rm --platform linux/arm64 image:tag python -c "import sys; print('test')"
```

### Security Testing (Buildx)
```bash
# Security scan results
# Available in GitHub Actions artifacts
# SARIF format for GitHub Security integration
```

## Production Readiness

### Current Status
- ✅ **Security scanning**: Semgrep integration
- ✅ **Multi-architecture**: AMD64 + ARM64 support
- ✅ **Code quality**: Pre-commit hooks
- ✅ **Testing**: Comprehensive validation
- ✅ **Registry push**: Enabled and working
- ✅ **Deployment**: Production ready
- ✅ **Latest tag**: Automatically created on main branch

### Next Steps
1. **Monitor builds**: Ensure builds complete successfully
2. **Test images**: Validate both AMD64 and ARM64 architectures
3. **Monitor security**: Review Semgrep results
4. **Performance optimization**: Monitor resource usage
5. **Verify latest tag**: Confirm `latest` tag is working correctly

## Troubleshooting

### Buildx Issues
```bash
# Check buildx availability
docker buildx version

# Create multi-arch builder
docker buildx create --name multiarch --driver docker-container --use

# Inspect image architectures
docker manifest inspect image:tag
```

### Build Issues
```bash
# Check build logs in GitHub Actions
# Verify registry permissions
# Review security scan results
```

### Security Issues
```bash
# Run Semgrep locally
docker run --rm -v $(pwd):/src semgrep/semgrep scan --config "p/default"

# Review SARIF results
# Check GitHub Security tab
```

## Configuration

### Environment Variables
```bash
# Build configuration
REGISTRY=ghcr.io
IMAGE_NAME=tw-haiven/haiven-mcp-server

# Security configuration
SEMGREP_CONFIG=p/default
SEMGREP_SEVERITY=ERROR
```

### GitHub Secrets
- `GITHUB_TOKEN`: Automatic (for registry access)
- `DISPATCH_HAIVEN_DEPLOYMENT_TOKEN`: For deployment notifications (optional)

## Best Practices

1. **Always run security scans**: Never skip Semgrep checks
2. **Test both architectures**: Validate AMD64 and ARM64
3. **Use pre-commit hooks**: Ensure code quality
4. **Monitor build times**: Optimize caching
5. **Review security results**: Address high severity issues
6. **Document changes**: Update this guide for new features

## Future Enhancements

- **ARM32 support**: Extend multi-architecture coverage
- **Performance monitoring**: Resource usage tracking
- **Security scanning**: Additional tools integration
- **Automated deployment**: CI/CD pipeline completion
- **Registry optimization**: Multi-arch manifest optimization
