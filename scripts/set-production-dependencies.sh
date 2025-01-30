#!/bin/bash
# scripts/configure-dependencies.sh

# Load environment variables
set -a
source .env
set +a

if [ "$ENVIRONMENT" = "production" ]; then
    # Check if we're on macOS or Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS version
        sed -i '' 's|{ path = "../common/src/solesearch_common", develop = true }|{ git = "https://github.com/SoleSearchAPI/common.git", tag = "'"$COMMON_VERSION"'" }|' pyproject.toml
    else
        # Linux version
        sed -i 's|{ path = "../common/src/solesearch_common", develop = true }|{ git = "https://github.com/SoleSearchAPI/common.git", tag = "'"$COMMON_VERSION"'" }|' pyproject.toml
    fi
    echo "Configured for production environment using version $COMMON_VERSION"
else
    echo "Using local development configuration"
fi

# Print the final dependency configuration
grep "solesearch-common" pyproject.toml
