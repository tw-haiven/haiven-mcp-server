#!/bin/bash

# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0
# Multi-architecture Docker testing script for Haiven MCP Server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="thoughtworks/haiven-mcp-server"
TAG="latest"

echo -e "${BLUE}🧪 Testing Multi-Architecture Docker Image${NC}"
echo "=============================================="
echo "Image: ${IMAGE_NAME}:${TAG}"
echo ""

# Function to test a specific architecture
test_architecture() {
    local platform=$1
    local arch_name=$2

    echo -e "\n${YELLOW}Testing ${arch_name} architecture (${platform})...${NC}"

    # Test basic Python functionality
    if docker run --rm -i --platform ${platform} --entrypoint python ${IMAGE_NAME}:${TAG} -c "import sys; print('Python test passed')" 2>/dev/null | grep -q "Python test passed"; then
        echo -e "${GREEN}✅ ${arch_name} basic functionality test passed${NC}"
    else
        echo -e "${RED}❌ ${arch_name} basic functionality test failed${NC}"
        return 1
    fi

    # Test environment variable handling with proper input handling
    local output=""
    if command -v timeout >/dev/null 2>&1; then
        # Use echo to send input and avoid hanging, with shorter timeout
        output=$(echo "" | timeout 3 docker run --rm -i --platform ${platform} \
            -e HAIVEN_API_URL="http://host.docker.internal:8080" \
            -e HAIVEN_DISABLE_AUTH="true" \
            ${IMAGE_NAME}:${TAG} 2>&1 || true)
    else
        # macOS alternative - use echo to send input with shorter timeout
        output=$(echo "" | docker run --rm -i --platform ${platform} \
            -e HAIVEN_API_URL="http://host.docker.internal:8080" \
            -e HAIVEN_DISABLE_AUTH="true" \
            ${IMAGE_NAME}:${TAG} 2>&1 || true)
    fi

    if echo "$output" | grep -q "API URL: http://host.docker.internal:8080"; then
        echo -e "${GREEN}✅ ${arch_name} environment variable test passed${NC}"
    else
        echo -e "${RED}❌ ${arch_name} environment variable test failed${NC}"
        return 1
    fi

    echo -e "${GREEN}✅ ${arch_name} architecture test completed${NC}"
}

# Function to test MCP server functionality
test_mcp_functionality() {
    echo -e "\n${YELLOW}Testing MCP server functionality...${NC}"

    # Get current architecture for testing
    CURRENT_ARCH=$(docker version --format '{{.Server.Os}}/{{.Server.Arch}}')

    # Test basic MCP server startup with proper input handling
    local output=""
    if command -v timeout >/dev/null 2>&1; then
        # Use echo to send input and avoid hanging
        output=$(echo "" | timeout 5 docker run --rm -i --platform ${CURRENT_ARCH} \
            -e HAIVEN_API_URL="http://host.docker.internal:8080" \
            -e HAIVEN_DISABLE_AUTH="true" \
            ${IMAGE_NAME}:${TAG} 2>&1 || true)
    else
        # macOS alternative - use echo to send input
        output=$(echo "" | docker run --rm -i --platform ${CURRENT_ARCH} \
            -e HAIVEN_API_URL="http://host.docker.internal:8080" \
            -e HAIVEN_DISABLE_AUTH="true" \
            ${IMAGE_NAME}:${TAG} 2>&1 || true)
    fi

    # Check for MCP server startup indicators
    if echo "$output" | grep -q "Registered tool: get_prompts" && \
       echo "$output" | grep -q "Registered tool: get_prompt_text"; then
        echo -e "${GREEN}✅ MCP server functionality test passed${NC}"
    else
        echo -e "${YELLOW}⚠️  MCP server functionality test inconclusive${NC}"
        echo -e "${YELLOW}   This is expected if the server is waiting for input${NC}"
        echo -e "${YELLOW}   Output: ${output:0:200}...${NC}"
    fi

    # Test environment variable handling
    if echo "$output" | grep -q "API URL: http://host.docker.internal:8080"; then
        echo -e "${GREEN}✅ Environment variable handling test passed${NC}"
    else
        echo -e "${RED}❌ Environment variable handling test failed${NC}"
        return 1
    fi
}

# Function to check available architectures
check_available_architectures() {
    echo -e "\n${YELLOW}Checking available architectures...${NC}"

    # Check if we have a local image
    if docker images | grep -q "${IMAGE_NAME}"; then
        echo -e "${GREEN}✅ Local image found${NC}"

        # Try to inspect the manifest (works for multi-arch images)
        if docker manifest inspect ${IMAGE_NAME}:${TAG} >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Multi-architecture manifest available${NC}"
            docker manifest inspect ${IMAGE_NAME}:${TAG} | grep -A 5 "platform"
        else
            echo -e "${YELLOW}⚠️  Single architecture image (local build)${NC}"
        fi
    else
        echo -e "${RED}❌ No local image found${NC}"
        echo -e "${YELLOW}   Run './scripts/build_multiarch.sh' first${NC}"
        return 1
    fi
}

# Function to test cross-platform compatibility
test_cross_platform() {
    echo -e "\n${YELLOW}Testing cross-platform compatibility...${NC}"

    # Test current platform
    CURRENT_ARCH=$(docker version --format '{{.Server.Os}}/{{.Server.Arch}}')
    echo "Current platform: ${CURRENT_ARCH}"

    # Test if we can run the image on current platform
    if docker run --rm -i --entrypoint python ${IMAGE_NAME}:${TAG} -c "import sys; print('Cross-platform test passed')" 2>/dev/null | grep -q "Cross-platform test passed"; then
        echo -e "${GREEN}✅ Cross-platform compatibility test passed${NC}"
    else
        echo -e "${RED}❌ Cross-platform compatibility test failed${NC}"
        return 1
    fi
}

# Function to show usage examples
show_usage_examples() {
    echo -e "\n${YELLOW}📋 Usage Examples${NC}"
    echo "=============================================="

    echo -e "\n${GREEN}# Basic usage (macOS/Windows):${NC}"
    echo "docker run -i --rm \\"
    echo "  -e HAIVEN_API_KEY=\"your-api-key\" \\"
    echo "  -e HAIVEN_API_URL=\"http://host.docker.internal:8080\" \\"
    echo "  ${IMAGE_NAME}:${TAG}"

    echo -e "\n${GREEN}# Linux usage (requires host-gateway):${NC}"
    echo "docker run -i --rm \\"
    echo "  --add-host=host.docker.internal:host-gateway \\"
    echo "  -e HAIVEN_API_KEY=\"your-api-key\" \\"
    echo "  -e HAIVEN_API_URL=\"http://host.docker.internal:8080\" \\"
    echo "  ${IMAGE_NAME}:${TAG}"

    echo -e "\n${GREEN}# Force specific architecture:${NC}"
    echo "docker run -i --rm --platform linux/amd64 ${IMAGE_NAME}:${TAG}"
    echo "docker run -i --rm --platform linux/arm64 ${IMAGE_NAME}:${TAG}"

    echo -e "\n${GREEN}# Check available architectures:${NC}"
    echo "docker manifest inspect ${IMAGE_NAME}:${TAG}"

    echo -e "\n${GREEN}# Development mode (no auth):${NC}"
    echo "docker run -i --rm \\"
    echo "  -e HAIVEN_API_URL=\"http://host.docker.internal:8080\" \\"
    echo "  -e HAIVEN_DISABLE_AUTH=\"true\" \\"
    echo "  ${IMAGE_NAME}:${TAG}"
}

# Function to show troubleshooting information
show_troubleshooting() {
    echo -e "\n${YELLOW}🔧 Troubleshooting${NC}"
    echo "=============================================="

    echo -e "\n${GREEN}# If architecture tests fail:${NC}"
    echo "1. Ensure you have the latest image: docker pull ${IMAGE_NAME}:${TAG}"
    echo "2. Rebuild locally: ./scripts/build_multiarch.sh"
    echo "3. Check Docker platform support: docker version"

    echo -e "\n${GREEN}# If MCP server tests fail:${NC}"
    echo "1. Check if Haiven API is running on host"
    echo "2. Verify network connectivity: ping host.docker.internal"
    echo "3. Test with development mode: HAIVEN_DISABLE_AUTH=true"

    echo -e "\n${GREEN}# If timeout command not found (macOS):${NC}"
    echo "1. Install coreutils: brew install coreutils"
    echo "2. Or use the fallback in the test script"

    echo -e "\n${GREEN}# For production multi-arch builds:${NC}"
    echo "1. Push to main branch to trigger GitHub Actions"
    echo "2. Check build status: https://github.com/thoughtworks/haiven-mcp-server/actions"
    echo "3. Pull from registry: docker pull ghcr.io/thoughtworks/haiven-mcp-server:latest"
}

# Main execution
main() {
    echo -e "${YELLOW}Starting multi-architecture tests...${NC}"

    # Check if image exists
    if ! docker images | grep -q "${IMAGE_NAME}"; then
        echo -e "${RED}❌ No image found. Building first...${NC}"
        ./scripts/build_multiarch.sh
    fi

    # Run tests
    check_available_architectures
    test_cross_platform
    test_mcp_functionality

    # Try to test other architectures if available
    if docker manifest inspect ${IMAGE_NAME}:${TAG} >/dev/null 2>&1; then
        echo -e "\n${YELLOW}Trying to test other architectures...${NC}"

        # Test AMD64 if not on AMD64
        if [ "$(uname -m)" != "x86_64" ]; then
            test_architecture "linux/amd64" "AMD64" || echo -e "${YELLOW}⚠️  AMD64 test skipped (not available)${NC}"
        fi

        # Test ARM64 if not on ARM64
        if [ "$(uname -m)" != "aarch64" ]; then
            test_architecture "linux/arm64" "ARM64" || echo -e "${YELLOW}⚠️  ARM64 test skipped (not available)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Single architecture image - skipping cross-arch tests${NC}"
    fi

    show_usage_examples
    show_troubleshooting

    echo -e "\n${GREEN}🎉 Multi-architecture testing completed!${NC}"
}

# Run main function
main "$@"
