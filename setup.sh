#!/usr/bin/env bash
# ==============================================================================
# UNIFIED AUDIT TOOL - Setup Script
# ==============================================================================
# This script:
#   1. Creates the proper directory structure
#   2. Creates all necessary __init__.py files
#   3. Verifies all required files are present
#   4. Installs Python dependencies
#   5. Adds the tool to your PATH for "run from anywhere" capability
#   6. Creates a convenient 'site-audit' command
#
# Usage:
#   chmod +x setup.sh
#   ./setup.sh
#
# After setup, run from anywhere with:
#   site-audit https://lastingchange.co --all
#
# Author: Built with Claude in BoodleBox
# Date: January 2026
# ==============================================================================

set -euo pipefail

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Tool name (this becomes the command you type)
TOOL_NAME="site-audit"

# Installation directory for the launcher script
INSTALL_DIR="$HOME/.local/bin"

# Shell config file
BASHRC="$HOME/.bashrc"
ZSHRC="$HOME/.zshrc"

# Get the directory where this setup script is located
# This is where all the audit tool files should be
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# ==============================================================================
# STEP 1: CREATE DIRECTORY STRUCTURE
# ==============================================================================

print_header "UNIFIED AUDIT TOOL - Setup"

echo "Tool location: $SCRIPT_DIR"
echo ""

print_info "Creating directory structure..."

# Create subdirectories if they don't exist
mkdir -p "$SCRIPT_DIR/palettes"
mkdir -p "$SCRIPT_DIR/plugins"
mkdir -p "$SCRIPT_DIR/reports"

print_success "Directory structure created"

# ==============================================================================
# STEP 2: CREATE __init__.py FILES
# ==============================================================================

print_info "Creating package __init__.py files..."

# Root __init__.py
cat > "$SCRIPT_DIR/__init__.py" << 'EOF'
"""
Unified Audit Tool - Web crawler and audit suite for design, SEO, and content.

A modular Python tool for analyzing websites against brand guidelines,
SEO best practices, and content quality standards.

Usage:
    from site_audit_tool import AuditEngine
    from site_audit_tool.plugins import DesignAuditor, SEOAuditor, ContentAuditor
"""

__version__ = "1.0.0"
__author__ = "Jonathan Sibley"
__description__ = "Unified web audit tool for design, SEO, and content analysis"
EOF
print_success "Created __init__.py (root)"

# palettes/__init__.py
cat > "$SCRIPT_DIR/palettes/__init__.py" << 'EOF'
"""
Brand palette definitions.

Each palette file defines approved colors, textures, and section-specific rules
for a particular website or brand.

Available palettes:
    - lasting_change: LASTING CHANGE executive coaching website
"""

# Import the default palette for convenience
try:
    from palettes.lasting_change import (
        BRAND_COLORS,
        BRAND_GRADIENTS,
        APPROVED_TEXTURES,
        APPROVED_BLEND_MODES,
        TEXTURE_OPACITY_RANGE,
        SECTION_RULES,
        get_color_name,
        get_section_rules,
        is_approved_color,
        is_approved_texture,
        get_all_approved_hex_codes,
    )
except ImportError:
    # Palette file not yet created
    pass

__all__ = [
    "BRAND_COLORS",
    "BRAND_GRADIENTS", 
    "APPROVED_TEXTURES",
    "APPROVED_BLEND_MODES",
    "TEXTURE_OPACITY_RANGE",
    "SECTION_RULES",
    "get_color_name",
    "get_section_rules",
    "is_approved_color",
    "is_approved_texture",
    "get_all_approved_hex_codes",
]
EOF
print_success "Created palettes/__init__.py"

# plugins/__init__.py
cat > "$SCRIPT_DIR/plugins/__init__.py" << 'EOF'
"""
Audit plugins for the Unified Audit Tool.

Each plugin handles a specific type of audit:
    - DesignAuditor: Colors, textures, blend modes, opacity
    - SEOAuditor: Meta tags, headings, Open Graph, Twitter Cards
    - ContentAuditor: Text extraction, word counts, placeholder detection
"""

try:
    from plugins.audit_design import DesignAuditor
except ImportError:
    DesignAuditor = None

try:
    from plugins.audit_seo import SEOAuditor
except ImportError:
    SEOAuditor = None

try:
    from plugins.audit_content import ContentAuditor
except ImportError:
    ContentAuditor = None

__all__ = [
    "DesignAuditor",
    "SEOAuditor",
    "ContentAuditor",
]

__version__ = "1.0.0"
EOF
print_success "Created plugins/__init__.py"

# reports/__init__.py
cat > "$SCRIPT_DIR/reports/__init__.py" << 'EOF'
"""
Report generation utilities for the Unified Audit Tool.

Supports multiple output formats:
    - CSV: Detailed results and summary statistics
    - HTML: Interactive reports with filtering
"""

try:
    from reports.csv_export import (
        export_to_csv,
        generate_summary_report,
        export_to_html,
    )
except ImportError:
    export_to_csv = None
    generate_summary_report = None
    export_to_html = None

__all__ = [
    "export_to_csv",
    "generate_summary_report",
    "export_to_html",
]
EOF
print_success "Created reports/__init__.py"

# ==============================================================================
# STEP 3: VERIFY REQUIRED FILES
# ==============================================================================

print_header "Verifying Required Files"

REQUIRED_FILES=(
    "main.py"
    "engine.py"
    "config.py"
    "palettes/lasting_change.py"
    "plugins/audit_design.py"
    "plugins/audit_seo.py"
    "plugins/audit_content.py"
    "reports/csv_export.py"
)

MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$SCRIPT_DIR/$file" ]]; then
        print_success "$file"
    else
        print_error "$file (MISSING)"
        MISSING_FILES+=("$file")
    fi
done

if [[ ${#MISSING_FILES[@]} -gt 0 ]]; then
    echo ""
    print_warning "Some files are missing. The tool may not work correctly."
    print_info "Please download the missing files and run setup again."
    echo ""
fi

# ==============================================================================
# STEP 4: INSTALL PYTHON DEPENDENCIES
# ==============================================================================

print_header "Installing Python Dependencies"

if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
    print_info "Installing from requirements.txt..."
    
    # Check if pip is available
    if command -v pip3 &> /dev/null; then
        pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet
        print_success "Dependencies installed"
    elif command -v pip &> /dev/null; then
        pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
        print_success "Dependencies installed"
    else
        print_warning "pip not found. Please install dependencies manually:"
        echo "    pip install requests beautifulsoup4 lxml"
    fi
else
    print_warning "requirements.txt not found. Installing core dependencies..."
    pip3 install requests beautifulsoup4 lxml --quiet 2>/dev/null || \
    pip install requests beautifulsoup4 lxml --quiet 2>/dev/null || \
    print_warning "Could not install dependencies. Please install manually."
fi

# ==============================================================================
# STEP 5: ADD TO PATH (Run from Anywhere)
# ==============================================================================

print_header "Setting Up 'Run from Anywhere'"

# Ensure the installation directory exists
mkdir -p "$INSTALL_DIR"

# Create the launcher script
cat > "$INSTALL_DIR/$TOOL_NAME" << EOF
#!/usr/bin/env bash
# ==============================================================================
# site-audit - Unified Audit Tool Launcher
# ==============================================================================
# This launcher allows you to run the audit tool from any directory.
# Generated by setup.sh on $(date)
# ==============================================================================

# Path to the actual tool
TOOL_DIR="$SCRIPT_DIR"

# Change to tool directory and run main.py with all arguments
cd "\$TOOL_DIR"
python3 main.py "\$@"
EOF

# Make the launcher executable
chmod +x "$INSTALL_DIR/$TOOL_NAME"
print_success "Created launcher: $INSTALL_DIR/$TOOL_NAME"

# Add to PATH if not already there
add_to_path() {
    local rc_file="$1"
    local shell_name="$2"
    
    if [[ -f "$rc_file" ]]; then
        if ! grep -q "export PATH=\"$INSTALL_DIR:\$PATH\"" "$rc_file" 2>/dev/null; then
            echo "" >> "$rc_file"
            echo "# Added by Unified Audit Tool setup script" >> "$rc_file"
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$rc_file"
            print_success "Added $INSTALL_DIR to PATH in $rc_file"
        else
            print_info "PATH already configured in $rc_file"
        fi
    fi
}

# Update bash config
add_to_path "$BASHRC" "bash"

# Update zsh config if it exists
if [[ -f "$ZSHRC" ]]; then
    add_to_path "$ZSHRC" "zsh"
fi

# Export PATH for current session
export PATH="$INSTALL_DIR:$PATH"

# ==============================================================================
# STEP 6: VERIFICATION
# ==============================================================================

print_header "Verification"

# Check if the command is available
if command -v "$TOOL_NAME" &> /dev/null; then
    print_success "'$TOOL_NAME' command is now available!"
    echo ""
    echo "    Location: $(which $TOOL_NAME)"
    echo ""
else
    print_warning "'$TOOL_NAME' installed but not in current session PATH"
    print_info "Run this command to activate: source ~/.bashrc"
fi

# ==============================================================================
# SUMMARY
# ==============================================================================

print_header "Setup Complete!"

echo "Directory structure:"
echo ""
echo "    $SCRIPT_DIR/"
echo "    ├── main.py              # CLI entry point"
echo "    ├── engine.py            # Web crawler engine"
echo "    ├── config.py            # Configuration"
echo "    ├── __init__.py          # Package init"
echo "    ├── requirements.txt"
echo "    ├── README.md"
echo "    │"
echo "    ├── palettes/"
echo "    │   ├── __init__.py"
echo "    │   └── lasting_change.py"
echo "    │"
echo "    ├── plugins/"
echo "    │   ├── __init__.py"
echo "    │   ├── audit_design.py"
echo "    │   ├── audit_seo.py"
echo "    │   └── audit_content.py"
echo "    │"
echo "    └── reports/"
echo "        ├── __init__.py"
echo "        └── csv_export.py"
echo ""

print_header "Usage Examples"

echo "Run from anywhere:"
echo ""
echo "    # Full audit"
echo "    $TOOL_NAME https://lastingchange.co --all"
echo ""
echo "    # Design audit only"
echo "    $TOOL_NAME https://lastingchange.co --type design"
echo ""
echo "    # SEO audit with custom output"
echo "    $TOOL_NAME https://lastingchange.co --type seo --output seo_report"
echo ""
echo "    # Crawl more pages"
echo "    $TOOL_NAME https://lastingchange.co --all --max-pages 100"
echo ""

if [[ ${#MISSING_FILES[@]} -gt 0 ]]; then
    print_warning "Remember to download the missing files listed above!"
fi

print_info "If '$TOOL_NAME' command is not found, run: source ~/.bashrc"
echo ""
