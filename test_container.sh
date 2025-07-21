#!/bin/bash

# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0
# Test script for Haiven MCP Server containerization (Multi-Architecture)

set -e

echo "🧪 Testing Haiven MCP Server Containerization (Multi-Architecture)"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_build() {
    echo -e "\n${YELLOW}1. Testing Docker build...${NC}"
    if docker build -t thoughtworks/haiven-mcp-server:test .; then
        echo -e "${GREEN}✅ Docker build successful${NC}"
        return 0
    else
        echo -e "${RED}❌ Docker build failed${NC}"
        return 1
    fi
}

test_basic_run() {
    echo -e "\n${YELLOW}2. Testing basic container startup...${NC}"
    timeout 5 docker run --rm -i thoughtworks/haiven-mcp-server:test > /dev/null 2>&1 || true
    if [ $? -eq 124 ]; then
        echo -e "${GREEN}✅ Container starts successfully (timeout expected for MCP server)${NC}"
        return 0
    else
        echo -e "${RED}❌ Container startup failed${NC}"
        return 1
    fi
}

test_environment_variables() {
    echo -e "\n${YELLOW}3. Testing environment variable handling...${NC}"
    output=$(timeout 3 docker run --rm -i \
        -e HAIVEN_API_URL="http://host.docker.internal:8080" \
        -e HAIVEN_DISABLE_AUTH="true" \
        thoughtworks/haiven-mcp-server:test 2>&1 || true)

    if echo "$output" | grep -q "API URL: http://host.docker.internal:8080"; then
        echo -e "${GREEN}✅ Environment variables handled correctly${NC}"
        return 0
    else
        echo -e "${RED}❌ Environment variables not handled correctly${NC}"
        echo "Output: $output"
        return 1
    fi
}

test_tool_registration() {
    echo -e "\n${YELLOW}4. Testing tool registration...${NC}"
    output=$(timeout 3 docker run --rm -i \
        -e HAIVEN_API_URL="http://host.docker.internal:8080" \
        -e HAIVEN_DISABLE_AUTH="true" \
        thoughtworks/haiven-mcp-server:test 2>&1 || true)

    if echo "$output" | grep -q "Registered tool: get_prompts" && \
       echo "$output" | grep -q "Registered tool: get_prompt_text"; then
        echo -e "${GREEN}✅ Tools registered successfully${NC}"
        return 0
    else
        echo -e "${RED}❌ Tool registration failed${NC}"
        echo "Output: $output"
        return 1
    fi
}

test_security() {
    echo -e "\n${YELLOW}5. Testing security (non-root user)...${NC}"
    user=$(docker run --rm -i thoughtworks/haiven-mcp-server:test whoami 2>/dev/null || echo "unknown")
    if [ "$user" = "haiven" ]; then
        echo -e "${GREEN}✅ Container runs as non-root user (haiven)${NC}"
        return 0
    else
        echo -e "${RED}❌ Container not running as non-root user (got: $user)${NC}"
        return 1
    fi
}

test_image_size() {
    echo -e "\n${YELLOW}6. Testing image size optimization...${NC}"
    size=$(docker images thoughtworks/haiven-mcp-server:test --format "{{.Size}}" | sed 's/[^0-9.]//g')
    echo "Image size: ${size}MB"
    if (( $(echo "$size < 500" | bc -l) )); then
        echo -e "${GREEN}✅ Image size is reasonable (< 500MB)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Image size is larger than expected (> 500MB)${NC}"
        return 0  # Not a failure, just a warning
    fi
}

test_multi_architecture() {
    echo -e "\n${YELLOW}7. Testing multi-architecture support...${NC}"

    # Get current platform
    CURRENT_PLATFORM=$(docker version --format '{{.Server.Os}}/{{.Server.Arch}}')
    echo "Current platform: ${CURRENT_PLATFORM}"

    # Test current platform
    if docker run --rm -i --platform ${CURRENT_PLATFORM} thoughtworks/haiven-mcp-server:test python -c "import sys; print('Current platform test passed')" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Current platform (${CURRENT_PLATFORM}) test passed${NC}"
        return 0
    else
        echo -e "${RED}❌ Current platform test failed${NC}"
        return 1
    fi
}

# Main test execution
main() {
    local failed_tests=0
    local total_tests=7

    test_build || ((failed_tests++))
    test_basic_run || ((failed_tests++))
    test_environment_variables || ((failed_tests++))
    test_tool_registration || ((failed_tests++))
    test_security || ((failed_tests++))
    test_image_size || ((failed_tests++))
    test_multi_architecture || ((failed_tests++))

    echo -e "\n${YELLOW}=============================================="
    echo "Test Results Summary"
    echo "=============================================="
    if [ $failed_tests -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed! ($total_tests/$total_tests)${NC}"
        echo -e "${GREEN}✅ Containerization is working correctly${NC}"
        return 0
    else
        echo -e "${RED}❌ $failed_tests test(s) failed ($((total_tests - failed_tests))/$total_tests passed)${NC}"
        return 1
    fi
}

# Run tests
main "$@"
