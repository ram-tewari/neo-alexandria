#!/bin/bash
# Model Rollback Script
# This script rolls back to a previous model version

set -e

# Parse arguments
VERSION=""
REASON="Manual rollback"
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION="$2"
            shift 2
            ;;
        --reason)
            REASON="$2"
            shift 2
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "========================================"
echo "Model Rollback Script"
echo "========================================"
echo ""

if [ -n "$VERSION" ]; then
    echo "Target version: $VERSION"
else
    echo "Target version: Previous production version"
fi
echo "Reason: $REASON"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to backend directory
cd "$BACKEND_DIR"

# Confirm rollback (unless forced)
if [ "$FORCE" = false ]; then
    echo "⚠ WARNING: This will rollback the production model"
    echo ""
    read -p "Are you sure you want to proceed? (yes/no): " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        echo "Rollback cancelled"
        exit 0
    fi
    echo ""
fi

# Step 1: Load previous version
echo "Step 1: Loading previous version..."
echo "----------------------------------------"

if [ -n "$VERSION" ]; then
    echo "Rolling back to specified version: $VERSION"
else
    echo "Rolling back to previous production version"
fi

echo ""

# Step 2: Switch traffic
echo "Step 2: Switching traffic..."
echo "----------------------------------------"

if [ -n "$VERSION" ]; then
    # Rollback to specific version using model versioning
    python scripts/deployment/model_versioning.py promote --version "$VERSION"
else
    # Rollback to previous version using rollback monitor
    python scripts/deployment/rollback_monitor.py rollback --reason "$REASON"
fi

echo ""
echo "✓ Traffic switched to previous version"
echo ""

# Step 3: Verify health
echo "Step 3: Verifying health..."
echo "----------------------------------------"

echo "Checking production metrics..."
python scripts/deployment/rollback_monitor.py metrics

echo ""
echo "✓ Health check complete"
echo ""

echo "========================================"
echo "✓ Rollback Complete!"
echo "========================================"
echo ""

if [ -n "$VERSION" ]; then
    echo "Rolled back to version: $VERSION"
else
    echo "Rolled back to previous production version"
fi
echo "Reason: $REASON"
echo ""

# Post-rollback steps
echo "Post-rollback checklist:"
echo "  [ ] Monitor metrics for stability"
echo "  [ ] Check error logs"
echo "  [ ] Investigate root cause"
echo "  [ ] Update incident report"
echo "  [ ] Notify team"
echo ""
