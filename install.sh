#!/usr/bin/env bash
# OASYS Invest — one-command installer.
# Clones (if needed), builds the Python engine venv, installs the frontend +
# Tauri shell, and drops an `oasys-invest` launcher on your PATH.
set -euo pipefail

REPO_URL="https://github.com/Olimdk/oasys-invest.git"
DEFAULT_HOME="$HOME/oasys-invest"

OASYS_INVEST_HOME="${OASYS_INVEST_HOME:-$DEFAULT_HOME}"

if [[ ! -d "$OASYS_INVEST_HOME" ]]; then
  echo "Cloning OASYS Invest -> $OASYS_INVEST_HOME"
  git clone "$REPO_URL" "$OASYS_INVEST_HOME"
fi

cd "$OASYS_INVEST_HOME"

echo "Setting up Python engine venv..."
if [[ ! -d backend/.venv ]]; then
  python3 -m venv backend/.venv
fi
# shellcheck disable=SC1091
source backend/.venv/bin/activate
pip install -q -r backend/requirements.txt
deactivate

echo "Installing frontend + Tauri CLI..."
npm install

echo "Building native desktop app (this may take a few minutes)..."
npm run tauri build

# Launcher
LAUNCHER="$OASYS_INVEST_HOME/oasys-invest-launcher.sh"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
# Launches the OASYS Invest desktop app.
DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
exec "\$DIR/src-tauri/target/release/oasys-invest" "\$@"
EOF
chmod +x "$LAUNCHER"

# Symlink onto PATH if we can.
if [[ -d "$HOME/.local/bin" ]]; then
  ln -sf "$LAUNCHER" "$HOME/.local/bin/oasys-invest"
  echo "Linked launcher -> $HOME/.local/bin/oasys-invest"
else
  echo "Add this to your PATH or run: $LAUNCHER"
fi

echo ""
echo "OASYS Invest installed. Run: oasys-invest"
