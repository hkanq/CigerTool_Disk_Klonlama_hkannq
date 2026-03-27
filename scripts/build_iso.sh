#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LB_DIR="$ROOT_DIR/iso/live-build"
SOURCE_MIRROR="$LB_DIR/config/includes.chroot/opt/cigertool"
DIST_DIR="$ROOT_DIR/dist"
OUTPUT_ISO="$DIST_DIR/cigertool.iso"
BUILD_LOG="$DIST_DIR/build.log"
CHECKSUM_FILE="$DIST_DIR/cigertool.iso.sha256"
CHROOT_DIR="$LB_DIR/chroot"
INVALID_SECURITY_SUITE_PART1="bookworm"
INVALID_SECURITY_SUITE_PART2="updates"
INVALID_SECURITY_SUITE="${INVALID_SECURITY_SUITE_PART1}/${INVALID_SECURITY_SUITE_PART2}"
CORRECT_SECURITY_SUITE="bookworm-security"

require_tool() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Eksik arac: $1" >&2
    exit 1
  fi
}

if [[ "${EUID}" -ne 0 ]]; then
  echo "Bu betigi root olarak calistirin: sudo ./scripts/build_iso.sh" >&2
  exit 1
fi

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "Bu betik yalnizca Linux ortaminda calisir." >&2
  exit 1
fi

require_tool lb
require_tool rsync
require_tool python3
require_tool sha256sum
require_tool grep

if command -v git >/dev/null 2>&1; then
  export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git -C "$ROOT_DIR" log -1 --format=%ct 2>/dev/null || date +%s)}"
else
  export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(date +%s)}"
fi

mkdir -p "$DIST_DIR"
rm -f "$OUTPUT_ISO" "$BUILD_LOG" "$CHECKSUM_FILE"

pushd "$LB_DIR" >/dev/null
  lb clean --purge || true
  ./auto/config
  while IFS= read -r -d '' file; do
    sed -i "s#${INVALID_SECURITY_SUITE}#${CORRECT_SECURITY_SUITE}#g" "$file"
  done < <(grep -RIlZ "$INVALID_SECURITY_SUITE" config || true)
  if grep -RIq "$INVALID_SECURITY_SUITE" config; then
    echo "Gecersiz Debian security suite kaldi: $INVALID_SECURITY_SUITE" >&2
    exit 1
  fi
  rm -rf "$SOURCE_MIRROR"
  mkdir -p "$SOURCE_MIRROR"
  rsync -a --delete \
    --exclude ".git" \
    --exclude ".github" \
    --exclude "__pycache__" \
    --exclude ".pytest_cache" \
    --exclude ".venv" \
    --exclude "dist" \
    --exclude "iso/live-build/cache" \
    "$ROOT_DIR/cigertool" \
    "$ROOT_DIR/docs" \
    "$ROOT_DIR/pyproject.toml" \
    "$ROOT_DIR/requirements.txt" \
    "$ROOT_DIR/README.md" \
    "$SOURCE_MIRROR/"
  lb build 2>&1 | tee "$BUILD_LOG"
popd >/dev/null

test -x "$CHROOT_DIR/usr/local/bin/cigertool-launch"
test -L "$CHROOT_DIR/etc/systemd/system/multi-user.target.wants/cigertool.service"
test "$(readlink "$CHROOT_DIR/etc/systemd/system/multi-user.target.wants/cigertool.service")" = "/etc/systemd/system/cigertool.service"
test -L "$CHROOT_DIR/etc/systemd/system/getty@tty1.service"
test "$(readlink "$CHROOT_DIR/etc/systemd/system/getty@tty1.service")" = "/dev/null"
if grep -R "$INVALID_SECURITY_SUITE" "$CHROOT_DIR/etc/apt" >/dev/null 2>&1; then
  echo "Chroot icinde gecersiz suite bulundu: $INVALID_SECURITY_SUITE" >&2
  exit 1
fi
grep -R "^deb http://security.debian.org/debian-security bookworm-security main$" "$CHROOT_DIR/etc/apt" >/dev/null

cp "$LB_DIR/live-image-amd64.hybrid.iso" "$OUTPUT_ISO"
sha256sum "$OUTPUT_ISO" | tee "$CHECKSUM_FILE"
echo "ISO hazir: $OUTPUT_ISO"
