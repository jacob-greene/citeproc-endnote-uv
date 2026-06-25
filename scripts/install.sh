#!/usr/bin/env bash
# Install asta-revision-workflow and its external tools.
#
#   pandoc  -> shipped via the pypandoc-binary wheel (installed with the package)
#   bip     -> Go binary (bipartite); installed here via `go install`
#   claude  -> Claude Code CLI; installed separately (npm), only checked here
#
# Usage:
#   scripts/install.sh            # editable install (uv pip install -e .)
#   scripts/install.sh --tool     # standalone tool install (uv tool install .)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

MODE="${1:-}"

echo "==> Installing Python package + bundled pandoc (pypandoc-binary)"
if [[ "$MODE" == "--tool" ]]; then
  uv tool install --force .
else
  uv pip install -e .
fi

echo "==> Installing bip (bipartite) via go install"
if command -v go >/dev/null 2>&1; then
  go install github.com/matsen/bipartite/cmd/bip@latest
  GOBIN="$(go env GOBIN)"; [[ -z "$GOBIN" ]] && GOBIN="$(go env GOPATH)/bin"
  echo "    bip installed to $GOBIN (ensure it is on your PATH)"
  echo "    configure ~/.config/bip/config.yml with nexus_path, s2_api_key, asta_api_key"
else
  echo "    WARNING: 'go' not found. Install Go 1.24+ then run:"
  echo "             go install github.com/matsen/bipartite/cmd/bip@latest"
  echo "    (or grab a prebuilt release from https://github.com/matsen/bipartite/releases)"
fi

echo "==> Checking claude (Claude Code) CLI"
if command -v claude >/dev/null 2>&1; then
  echo "    claude: $(claude --version 2>&1 | head -1)"
else
  echo "    WARNING: 'claude' not found. Install Claude Code: https://docs.claude.com/claude-code"
fi

echo "==> Done. Verify with: asta-revision --help"
