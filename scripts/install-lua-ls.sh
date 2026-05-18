#!/usr/bin/env bash
# install-lua-ls.sh — Download and install the latest lua-language-server binary.
#
# Default: installs to ~/.local/opt/lua-language-server with a symlink at
#          ~/.local/bin/lua-language-server
# With sudo: installs to /usr/local/opt/ and /usr/local/bin/

set -euo pipefail

REPO="LuaLS/lua-language-server"

if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    INSTALL_DIR="/usr/local/opt/lua-language-server"
    BIN_DIR="/usr/local/bin"
else
    INSTALL_DIR="${HOME}/.local/opt/lua-language-server"
    BIN_DIR="${HOME}/.local/bin"
fi

# Detect OS and architecture
OS="$(uname -s)"
ARCH="$(uname -m)"

case "${OS}" in
    Linux)  PLATFORM="linux" ;;
    Darwin) PLATFORM="darwin" ;;
    *)      echo "Unsupported OS: ${OS}" >&2; exit 1 ;;
esac

case "${ARCH}" in
    x86_64)          ARCH_TAG="x64" ;;
    aarch64 | arm64) ARCH_TAG="arm64" ;;
    *)               echo "Unsupported architecture: ${ARCH}" >&2; exit 1 ;;
esac

# Resolve latest release tag via GitHub API
echo "Fetching latest lua-language-server release..."
VERSION="$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
    | grep '"tag_name"' | head -1 \
    | sed 's/.*"tag_name": *"\([^"]*\)".*/\1/')"

if [[ -z "${VERSION}" ]]; then
    echo "Failed to fetch latest release version." >&2
    exit 1
fi

echo "Latest version: ${VERSION}"

# Build download URL (tarball name uses version without leading 'v')
VERSION_NUM="${VERSION#v}"
TARBALL="lua-language-server-${VERSION_NUM}-${PLATFORM}-${ARCH_TAG}.tar.gz"
URL="https://github.com/${REPO}/releases/download/${VERSION}/${TARBALL}"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

echo "Downloading ${TARBALL}..."
curl -fsSL --progress-bar -o "${TMP_DIR}/${TARBALL}" "${URL}"

echo "Installing to ${INSTALL_DIR}..."
rm -rf "${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"
tar -xzf "${TMP_DIR}/${TARBALL}" -C "${INSTALL_DIR}"

mkdir -p "${BIN_DIR}"
ln -sf "${INSTALL_DIR}/bin/lua-language-server" "${BIN_DIR}/lua-language-server"

echo ""
echo "Installed lua-language-server ${VERSION}"
echo "  Binary: ${BIN_DIR}/lua-language-server"
echo ""

if [[ ":${PATH}:" != *":${BIN_DIR}:"* ]]; then
    echo "NOTE: Add ${BIN_DIR} to your PATH:"
    echo "  export PATH=\"\${PATH}:${BIN_DIR}\""
    echo "  (add this to your ~/.bashrc or ~/.zshrc)"
fi
