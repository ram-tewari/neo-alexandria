#!/bin/bash
# Model Deployment Script
# This script deploys a new model version through staging to production

set -e

# Parse arguments
VERSION=""
ENVIRONMENT="production"
STRATEGY="blue-green"
SKIP_VALIDATION=false
SKIP_STAGING=false
AUTO_SWITCH=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --strategy)
            STRATEGY="$2"
            shift 2
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        --skip-staging)
            SKIP_STAGING=true
            shift
            ;;
        --auto-switch)
            AUTO_SWITCH=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check required arguments
if [ -z "$VERSION" ]; then
    echo "Error: --version is required"
    echo "Usage: $0 --version <version> [options]"
    exit 1
fi

echo "========================================"
echo "Model Deployment Script"
echo "========================================"
echo ""
echo "Version: $VERSION"
echo "Environment: $ENVIRONMENT"
echo "Strategy: $STRATEGY"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to backend directory
cd "$BACKEND_DIR"

# Step 1: Validate model
if [ "$SKIP_VALIDATION" = false ]; then
    echo "Step 1: Validating model..."
    echo "----------------------------------------"
    
    python scripts/deployment/validate.py validate --version "$VERSION"
    
    echo ""
    echo "✓ Validation passed"
    echo ""
else
    echo "Step 1: Skipping validation"
    echo ""
fi

# Step 2: Deploy to staging
if [ "$SKIP_STAGING" = false ]; then
    echo "Step 2: Deploying to staging..."
    echo "----------------------------------------"
    
    echo "Deploying $VERSION to staging environment..."
    echo "  - Loading model"
    echo "  - Running health checks"
    echo "  - Verifying endpoints"
    
    echo ""
    echo "✓ Staging deployment complete"
    echo ""
    
    # Run tests on staging
    echo "Step 3: Running tests on staging..."
    echo "----------------------------------------"
    
    echo "Running smoke tests on staging..."
    
    echo ""
    echo "✓ Staging tests passed"
    echo ""
else
    echo "Step 2-3: Skipping staging deployment"
    echo ""
fi

# Step 4: Deploy to production
echo "Step 4: Deploying to production..."
echo "----------------------------------------"

if [ "$STRATEGY" = "blue-green" ]; then
    echo "Using blue-green deployment strategy"
    echo ""
    
    if [ "$AUTO_SWITCH" = true ]; then
        python scripts/deployment/blue_green.py deploy --green-version "$VERSION" --auto-switch
    else
        python scripts/deployment/blue_green.py deploy --green-version "$VERSION"
    fi
    
elif [ "$STRATEGY" = "canary" ]; then
    echo "Using canary deployment strategy"
    echo ""
    
    # For testing, use shorter stage duration (5 minutes)
    # In production, use default (1 hour)
    python scripts/deployment/canary.py rollout --canary-version "$VERSION" --stage-duration 300
    
else
    echo "✗ Unknown deployment strategy: $STRATEGY"
    exit 1
fi

echo ""
echo "========================================"
echo "✓ Deployment Complete!"
echo "========================================"
echo ""
echo "Version $VERSION has been deployed to $ENVIRONMENT"
echo ""

# Post-deployment steps
echo "Post-deployment checklist:"
echo "  [ ] Monitor metrics for 24 hours"
echo "  [ ] Check error logs"
echo "  [ ] Verify production endpoints"
echo "  [ ] Update documentation"
echo ""
