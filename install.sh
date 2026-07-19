#!/usr/bin/env bash
# OASYS Invest — one-command installer.
# Downloads the latest release bundle and sets up the Python engine.
set -euo pipefail

REPO="Olimdk/oasys-invest"
INSTALL_PREFIX="${INSTALL_PREFIX:-/usr/local}"

echo "OASYS Invest installer"

# 1. Pick the right asset for this system.
if command -v apt-get >/dev/null 2>&1; then
  ASSET_PATTERN="\.deb$"
  echo "Detected Debian/Ubuntu — will install the .deb package."
elif command -v dnf >/dev/null 2>&1 || command -v yum >/dev/null 2>&1; then
  ASSET_PATTERN="\.rpm$"
  echo "Detected Fedora/RHEL — .rpm not published yet, falling back to AppImage."
  ASSET_PATTERN="\.AppImage$"
else
  ASSET_PATTERN="\.AppImage$"
  echo "Using the AppImage (portable)."
fi

# 2. Resolve the latest release download URL via the GitHub API.
ASSET_URL=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
  | grep -o "https://github.com/${REPO}/releases/download/[^ \"']*${ASSET_PATTERN}" \
  | head -1)

if [ -z "${ASSET_URL:-}" ]; then
  echo "ERROR: could not find a release asset for this system." >&2
  exit 1
fi

echo "Downloading: ${ASSET_URL}"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
curl -fLSL "${ASSET_URL}" -o "${TMP}/oasys-invest-asset"

# 3. Install.
if [[ "${ASSET_URL}" == *.deb ]]; then
  sudo apt-get install -y "${TMP}/oasys-invest-asset" || sudo dpkg -i "${TMP}/oasys-invest-asset"
  BACKEND_DIR="/usr/lib/OASYS Invest/_up_/backend"
elif [[ "${ASSET_URL}" == *.AppImage ]]; then
  chmod +x "${TMP}/oasys-invest-asset"
  sudo mv "${TMP}/oasys-invest-asset" "${INSTALL_PREFIX}/bin/oasys-invest.AppImage"
  sudo ln -sf "${INSTALL_PREFIX}/bin/oasys-invest.AppImage" "${INSTALL_PREFIX}/bin/oasys-invest"
  BACKEND_DIR="${INSTALL_PREFIX}/bin/oasys-invest.AppImage"
  # AppImage backend lives next to the executable when extracted; for portability
  # we set up the venv in the user repo location instead:
  BACKEND_DIR="$HOME/oasys-invest/backend"
  mkdir -p "$HOME/oasys-invest"
fi

# 4. Ensure the Python engine venv exists (the bundle ships source, not the venv).
echo "Setting up the Python engine virtualenv…"
if [ -d "${BACKEND_DIR}" ] && [ -f "${BACKEND_DIR}/requirements.txt" ]; then
  if [ ! -d "${BACKEND_DIR}/.venv" ]; then
    python3 -m venv "${BACKEND_DIR}/.venv"
  fi
  # shellcheck disable=SC1091
  source "${BACKEND_DIR}/.venv/bin/activate"
  pip install -q -r "${BACKEND_DIR}/requirements.txt"
  deactivate
fi

echo ""
echo "OASYS Invest installed. Launch it from your applications menu (OASYS Invest)."
