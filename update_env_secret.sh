#!/bin/bash

# Set the repository secret from the local production environment file
# Requires GitHub CLI (gh) to be installed and authenticated

# Default values
ENV_FILE="prod.env"
SECRET_NAME="PRODUCTION_ENV_FILE"
REPO="SoleSearchAPI/api"

# Parse command line arguments
while (("$#")); do
    case "$1" in
    --file)
        ENV_FILE="$2"
        shift 2
        ;;
    --secret)
        SECRET_NAME="$2"
        shift 2
        ;;
    --repo)
        REPO="$2"
        shift 2
        ;;
    *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Check if env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file '$ENV_FILE' not found"
    exit 1
fi

# Set the repository parameter if provided
REPO_PARAM=""
if [ -n "$REPO" ]; then
    REPO_PARAM="--repo $REPO"
fi

# Update the secret using GitHub CLI
echo "Setting GitHub secret '$SECRET_NAME' from file '$ENV_FILE'..."
gh secret set "$SECRET_NAME" $REPO_PARAM <"$ENV_FILE"

if [ $? -eq 0 ]; then
    echo "Secret '$SECRET_NAME' updated successfully!"
else
    echo "Failed to update secret. Make sure GitHub CLI is installed and you're authenticated."
    exit 1
fi
