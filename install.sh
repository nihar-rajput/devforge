#!/usr/bin/env bash
# ==============================================================================
# DevForge — Universal Cross-Platform Installer for macOS & Linux
# ==============================================================================
set -e

echo "⚡ Installing DevForge Platform for $(uname -s) ($(uname -m))..."

INSTALL_DIR="$HOME/.devforge"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

echo "📦 Cloning latest DevForge release..."
git clone --depth 1 https://github.com/nihar-rajput/devforge.git "$INSTALL_DIR/repo" 2>/dev/null || (cd "$INSTALL_DIR/repo" && git pull)

echo "🔧 Configuring Python environment..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip > /dev/null
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/repo/backend/requirements.txt" > /dev/null

echo "🚀 Linking DevForge CLI executable..."
cat << 'EOF' > "$BIN_DIR/devforge"
#!/usr/bin/env bash
export PYTHONPATH="$HOME/.devforge/repo/backend"
exec "$HOME/.devforge/venv/bin/python" "$HOME/.devforge/repo/backend/src/cli/main.py" "$@"
EOF

chmod +x "$BIN_DIR/devforge"

# Update PATH in shell profile
SHELL_PROFILE=""
if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_PROFILE="$HOME/.bashrc"
else
    SHELL_PROFILE="$HOME/.profile"
fi

if ! grep -q "$BIN_DIR" "$SHELL_PROFILE" 2>/dev/null; then
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_PROFILE"
    echo "✨ Added $BIN_DIR to $SHELL_PROFILE"
fi

echo "=============================================================================="
echo "🎉 DevForge successfully installed!"
echo "Run 'devforge --help' or 'devforge install python' to start using DevForge."
echo "=============================================================================="
