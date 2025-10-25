#!/bin/bash

# HR Job Analysis Engine Setup Script

echo "🚀 Setting up HR Job Analysis Engine..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ pip3 found"

# Create virtual environment (optional but recommended)
read -p "Create a virtual environment? (recommended) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
    echo "💡 To activate it later, run: source venv/bin/activate"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Set up environment file
if [ ! -f .env ]; then
    echo "⚙️  Setting up environment configuration..."
    cp .env.template .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env and add your Google Gemini API key"
else
    echo "✅ .env file already exists"
fi

# Create output directory
mkdir -p output
echo "✅ Created output directory"

# Test basic import (if possible)
echo "🧪 Testing basic functionality..."
if python3 -c "import sys; sys.path.append('src'); import job_analyzer; print('✅ Core modules can be imported')" 2>/dev/null; then
    echo "✅ Basic functionality test passed"
else
    echo "⚠️  Import test failed - this is expected if dependencies aren't available in the environment"
fi

echo ""
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Get your Google Gemini API key from: https://makersuite.google.com/app/apikey"
echo "2. Edit the .env file and add your API key:"
echo "   GEMINI_API_KEY=your_api_key_here"
echo "3. Test the engine:"
echo "   python3 main.py --input examples/sample_job_description.txt"
echo ""
echo "For more information, see README.md"