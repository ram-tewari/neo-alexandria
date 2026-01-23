#!/bin/bash
# Neo Alexandria Edge Worker Setup Script for Linux/macOS
# This script sets up the edge worker environment and optionally installs it as a system service

set -e

echo "=========================================="
echo "Neo Alexandria Edge Worker Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "ERROR: Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi
echo "✓ Python $PYTHON_VERSION detected"
echo ""

# Check for CUDA
echo "Checking CUDA availability..."
if command -v nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    echo ""
    CUDA_AVAILABLE=true
else
    echo "⚠ No NVIDIA GPU detected. Worker will run on CPU (slower)."
    echo ""
    CUDA_AVAILABLE=false
fi

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing edge worker dependencies..."
pip install --upgrade pip
pip install -r requirements-edge.txt
echo "✓ Dependencies installed"
echo ""

# Verify PyTorch installation
echo "Verifying PyTorch installation..."
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
echo ""

# Check for .env.edge file
echo "Checking configuration..."
if [ ! -f ".env.edge" ]; then
    echo "⚠ .env.edge file not found. Creating from template..."
    if [ -f ".env.edge.template" ]; then
        cp .env.edge.template .env.edge
        echo "✓ Created .env.edge from template"
        echo ""
        echo "IMPORTANT: Edit .env.edge and add your credentials:"
        echo "  - UPSTASH_REDIS_URL"
        echo "  - UPSTASH_REDIS_TOKEN"
        echo "  - QDRANT_URL"
        echo "  - QDRANT_API_KEY"
        echo ""
    else
        echo "ERROR: .env.edge.template not found"
        exit 1
    fi
else
    echo "✓ .env.edge file found"
    echo ""
fi

# Test worker startup
echo "Testing worker startup..."
if python3 -c "from worker import main; print('✓ Worker imports successfully')"; then
    echo "✓ Worker is ready to run"
else
    echo "ERROR: Worker failed to import. Check dependencies."
    exit 1
fi
echo ""

# Ask about service installation
echo "=========================================="
echo "Service Installation (Optional)"
echo "=========================================="
echo ""
echo "Would you like to install the edge worker as a system service?"
echo "This will make it start automatically on boot."
echo ""
read -p "Install as service? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Creating systemd service..."
        
        # Get absolute paths
        WORKER_DIR=$(pwd)
        PYTHON_PATH="$WORKER_DIR/.venv/bin/python3"
        
        # Create systemd service file
        sudo tee /etc/systemd/system/neo-alexandria-worker.service > /dev/null <<EOF
[Unit]
Description=Neo Alexandria Edge Worker
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORKER_DIR
Environment="PATH=$WORKER_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PYTHON_PATH worker.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
        
        # Reload systemd and enable service
        sudo systemctl daemon-reload
        sudo systemctl enable neo-alexandria-worker.service
        
        echo "✓ Systemd service installed"
        echo ""
        echo "Service commands:"
        echo "  Start:   sudo systemctl start neo-alexandria-worker"
        echo "  Stop:    sudo systemctl stop neo-alexandria-worker"
        echo "  Status:  sudo systemctl status neo-alexandria-worker"
        echo "  Logs:    sudo journalctl -u neo-alexandria-worker -f"
        echo ""
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Creating launchd service..."
        
        # Get absolute paths
        WORKER_DIR=$(pwd)
        PYTHON_PATH="$WORKER_DIR/.venv/bin/python3"
        PLIST_PATH="$HOME/Library/LaunchAgents/com.neoalexandria.worker.plist"
        
        # Create launchd plist file
        cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.neoalexandria.worker</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>worker.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$WORKER_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$WORKER_DIR/worker.log</string>
    <key>StandardErrorPath</key>
    <string>$WORKER_DIR/worker.error.log</string>
</dict>
</plist>
EOF
        
        # Load the service
        launchctl load "$PLIST_PATH"
        
        echo "✓ Launchd service installed"
        echo ""
        echo "Service commands:"
        echo "  Start:   launchctl start com.neoalexandria.worker"
        echo "  Stop:    launchctl stop com.neoalexandria.worker"
        echo "  Unload:  launchctl unload $PLIST_PATH"
        echo "  Logs:    tail -f $WORKER_DIR/worker.log"
        echo ""
    else
        echo "⚠ Unsupported OS for automatic service installation"
        echo "You can run the worker manually with: python3 worker.py"
    fi
else
    echo "Skipping service installation."
    echo ""
fi

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env.edge with your credentials (if not done already)"
echo "2. Run the worker:"
echo "   source .venv/bin/activate"
echo "   python3 worker.py"
echo ""
echo "Or if installed as service, start it with the commands shown above."
echo ""
