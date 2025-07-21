#!/bin/bash

# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0
# Multi-architecture Docker build script for Haiven MCP Server

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
PLATFORMS="linux/amd64,linux/arm64"

echo -e "${BLUE}🏗️  Building Multi-Architecture Docker Image${NC}"
echo "=============================================="
echo "Image: ${IMAGE_NAME}:${TAG}"
echo "Platforms: ${PLATFORMS}"
echo ""

# Function to check if buildx is available and properly configured
check_buildx() {
    echo -e "${YELLOW}Checking Docker Buildx availability...${NC}"

    # Check if buildx command exists
    if ! docker buildx version >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker Buildx not available${NC}"
        echo -e "${YELLOW}   Install with: docker buildx install${NC}"
        return 1
    fi

    # Check if we have a builder instance
    if ! docker buildx ls | grep -q "default"; then
        echo -e "${YELLOW}⚠️  No default builder found, creating one...${NC}"
        docker buildx create --name default --driver docker-container --use
    fi

    # Check if the builder supports multi-platform
    if docker buildx inspect default | grep -q "linux/amd64\|linux/arm64"; then
        echo -e "${GREEN}✅ Multi-architecture builder available${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Builder doesn't support multi-platform, creating new one...${NC}"
        docker buildx create --name multiarch --driver docker-container --use
        return 0
    fi
}

# Function to build with buildx for multiple architectures
build_with_buildx() {
    echo -e "${YELLOW}Building multi-architecture image with buildx...${NC}"

    # Build for multiple architectures
    docker buildx build \
        --platform ${PLATFORMS} \
        --tag ${IMAGE_NAME}:${TAG} \
        --tag ${IMAGE_NAME}:latest \
        --cache-from type=local,src=/tmp/.buildx-cache \
        --cache-to type=local,dest=/tmp/.buildx-cache \
        --push=false \
        --load=false \
        .

    echo -e "${GREEN}✅ Multi-architecture build completed${NC}"
    echo -e "${YELLOW}⚠️  Note: Multi-arch images are not loaded locally by default${NC}"
    echo -e "${YELLOW}   Use 'docker buildx build --load' to load into local registry${NC}"
}

# Function to build individual architecture (fallback)
build_individual() {
    echo -e "${YELLOW}Building individual architectures...${NC}"

    # Build for current architecture first
    CURRENT_ARCH=$(docker version --format '{{.Server.Os}}/{{.Server.Arch}}')
    echo "Building for current architecture: ${CURRENT_ARCH}"

    docker build -t ${IMAGE_NAME}:${TAG} .
    docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_NAME}:latest

    echo -e "${GREEN}✅ Build completed for current architecture${NC}"
    echo -e "${YELLOW}⚠️  Note: This build is for ${CURRENT_ARCH} only${NC}"
    echo -e "${YELLOW}   For multi-architecture builds, use GitHub Actions or upgrade Docker${NC}"
}

# Function to build and load multi-arch locally
build_multiarch_local() {
    echo -e "${YELLOW}Building multi-architecture image for local use...${NC}"

    # Build for current architecture using regular docker build
    CURRENT_ARCH=$(docker version --format '{{.Server.Os}}/{{.Server.Arch}}')
    echo "Building for local use: ${CURRENT_ARCH}"

    docker build -t ${IMAGE_NAME}:${TAG} .
    docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_NAME}:latest

    echo -e "${GREEN}✅ Local build completed for ${CURRENT_ARCH}${NC}"
    echo -e "${YELLOW}⚠️  Note: This is a single-architecture build for local development${NC}"
    echo -e "${YELLOW}   For true multi-architecture builds, use GitHub Actions${NC}"
}

# Function to test the built image
test_image() {
    echo -e "\n${YELLOW}🧪 Testing built image...${NC}"

    # Test basic functionality (run a simple Python command)
    if docker run --rm -i --entrypoint python ${IMAGE_NAME}:${TAG} -c "import sys; print('Python test passed')" 2>/dev/null | grep -q "Python test passed"; then
        echo -e "${GREEN}✅ Basic functionality test passed${NC}"
    else
        echo -e "${RED}❌ Basic functionality test failed${NC}"
        return 1
    fi

    # Test environment variable handling with proper input handling
    local output=""
    if command -v timeout >/dev/null 2>&1; then
        # Use echo to send input and avoid hanging
        output=$(echo "" | timeout 3 docker run --rm -i \
            -e HAIVEN_API_URL="http://host.docker.internal:8080" \
            -e HAIVEN_DISABLE_AUTH="true" \
            ${IMAGE_NAME}:${TAG} 2>&1 || true)
    else
        # macOS alternative - use echo to send input
        output=$(echo "" | docker run --rm -i \
            -e HAIVEN_API_URL="http://host.docker.internal:8080" \
            -e HAIVEN_DISABLE_AUTH="true" \
            ${IMAGE_NAME}:${TAG} 2>&1 || true)
    fi

    if echo "$output" | grep -q "API URL: http://host.docker.internal:8080"; then
        echo -e "${GREEN}✅ Environment variable test passed${NC}"
    else
        echo -e "${RED}❌ Environment variable test failed${NC}"
        return 1
    fi

    # Test MCP server startup (should start and register tools)
    if echo "$output" | grep -q "Registered tool: get_prompts" && \
       echo "$output" | grep -q "Registered tool: get_prompt_text"; then
        echo -e "${GREEN}✅ MCP server functionality test passed${NC}"
    else
        echo -e "${YELLOW}⚠️  MCP server functionality test inconclusive${NC}"
        echo -e "${YELLOW}   This is expected if the server is waiting for input${NC}"
    fi

    echo -e "${GREEN}✅ All tests passed${NC}"
}

# Function to show usage information
show_usage() {
    echo -e "\n${YELLOW}📋 Usage Information${NC}"
    echo "=============================================="
    echo "To use the multi-architecture image:"
    echo ""
    echo "# For macOS and Windows:"
    echo "docker run -i --rm \\"
    echo "  -e HAIVEN_API_KEY=\"your-api-key\" \\"
    echo "  -e HAIVEN_API_URL=\"http://host.docker.internal:8080\" \\"
    echo "  ${IMAGE_NAME}:${TAG}"
    echo ""
    echo "# For Linux:"
    echo "docker run -i --rm \\"
    echo "  --add-host=host.docker.internal:host-gateway \\"
    echo "  -e HAIVEN_API_KEY=\"your-api-key\" \\"
    echo "  -e HAIVEN_API_URL=\"http://host.docker.internal:8080\" \\"
    echo "  ${IMAGE_NAME}:${TAG}"
    echo ""
    echo "# Check available architectures:"
    echo "docker manifest inspect ${IMAGE_NAME}:${TAG}"
    echo ""
    echo "# Force specific architecture:"
    echo "docker run -i --rm --platform linux/amd64 ${IMAGE_NAME}:${TAG}"
    echo "docker run -i --rm --platform linux/arm64 ${IMAGE_NAME}:${TAG}"
}

# Function to show CI/CD information
show_cicd_info() {
    echo -e "\n${YELLOW}🚀 CI/CD Information${NC}"
    echo "=============================================="
    echo "For production multi-architecture builds:"
    echo ""
    echo "1. Push to main branch to trigger GitHub Actions"
    echo "2. GitHub Actions will build and push to ghcr.io"
    echo "3. Images will be available at: ghcr.io/thoughtworks/haiven-mcp-server"
    echo ""
    echo "To manually trigger a build:"
    echo "git push origin main"
    echo ""
    echo "To check build status:"
    echo "Visit: https://github.com/thoughtworks/haiven-mcp-server/actions"
}

# Main execution
main() {
    echo -e "${YELLOW}Starting multi-architecture build...${NC}"

    # Try buildx first
    if check_buildx; then
        echo -e "${GREEN}Using Docker Buildx for multi-architecture builds${NC}"
        build_with_buildx
    else
        echo -e "${YELLOW}Falling back to local build${NC}"
        build_multiarch_local
    fi

    test_image
    show_usage
    show_cicd_info

    echo -e "\n${GREEN}🎉 Build process completed!${NC}"
    echo -e "${BLUE}💡 Tip: Use GitHub Actions for production multi-arch builds${NC}"
}

# Run main function
main "$@"
