#!/usr/bin/env bash
set -e

# --- Colors & Logging ---
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_RED="\033[1;31m"
C_GREEN="\033[1;32m"
C_YELLOW="\033[1;33m"
C_CYAN="\033[1;36m"
C_MAGENTA="\033[1;35m"

log_info()   { echo -e "${C_CYAN}[info]${C_RESET} $1"; }
log_notice() { echo -e "${C_YELLOW}[notice]${C_RESET} $1"; }
log_ok()     { echo -e "${C_GREEN}[ok]${C_RESET} $1"; }
log_warn()   { echo -e "${C_YELLOW}[warning]${C_RESET} $1"; }
log_err()    { echo -e "${C_RED}[error]${C_RESET} $1" >&2; }
log_step()   { echo -e "\n${C_MAGENTA}==>${C_RESET} ${C_BOLD}$1${C_RESET}"; }

# --- Configuration ---
APP_NAME="YouTube-Downloader"
ENTRY_POINT="code/main.py"
FOLLOW_IMPORT_PACKAGES="rich textual"
HEAVY_FOLLOW_PACKAGES=""
HEAVY_EXCLUDE_SUBMODULES=""
EXCLUDE_STDLIB="unittest,pydoc,doctest,tkinter,test,yt_dlp"
OUTPUT_DIR="dist"
NEEDS_FFMPEG="yes"

if [ -z "$VIRTUAL_ENV" ]; then
  log_err "venv not activated. Run: source .venv/bin/activate"
  exit 1
fi

log_info "Updating compilation tools (nuitka, patchelf, etc.)..."
pip install -q -U nuitka ordered-set zstandard patchelf

BUNDLE_DIR="$(mktemp -d)"
trap 'rm -rf "$BUNDLE_DIR"' EXIT

DATA_FILE_FLAGS=()

if [ "$NEEDS_FFMPEG" = "yes" ]; then
  log_step "Preparing portable ffmpeg + ffprobe"
  pip install -q -U portable-ffmpeg
  python -c 'from portable_ffmpeg import get_ffmpeg; f, p = get_ffmpeg(); open(".ffmpeg_path.tmp","w").write(str(f)); open(".ffprobe_path.tmp","w").write(str(p))'
  FFMPEG_SRC="$(cat .ffmpeg_path.tmp)"
  FFPROBE_SRC="$(cat .ffprobe_path.tmp)"
  rm -f .ffmpeg_path.tmp .ffprobe_path.tmp
  cp "$FFMPEG_SRC" "$BUNDLE_DIR/ffmpeg"
  cp "$FFPROBE_SRC" "$BUNDLE_DIR/ffprobe"
  chmod +x "$BUNDLE_DIR/ffmpeg" "$BUNDLE_DIR/ffprobe"
  DATA_FILE_FLAGS+=(--include-data-files="$BUNDLE_DIR/ffmpeg=ffmpeg")
  DATA_FILE_FLAGS+=(--include-data-files="$BUNDLE_DIR/ffprobe=ffprobe")
  log_ok "ffmpeg bundled successfully"
fi

rm -rf "$OUTPUT_DIR"

INCLUDE_FLAGS=()
for pkg in $FOLLOW_IMPORT_PACKAGES; do
  INCLUDE_FLAGS+=(--include-package="$pkg")
done
FOLLOW_FLAGS=()
for pkg in $HEAVY_FOLLOW_PACKAGES; do
  FOLLOW_FLAGS+=(--follow-import-to="$pkg")
done
HEAVY_EXCLUDE_FLAGS=()
if [ -n "$HEAVY_EXCLUDE_SUBMODULES" ]; then
  HEAVY_EXCLUDE_FLAGS+=(--nofollow-import-to="$HEAVY_EXCLUDE_SUBMODULES")
fi

log_step "Compiling with Nuitka"
python -m nuitka "$ENTRY_POINT" \
  --standalone \
  --output-dir="$OUTPUT_DIR" \
  --output-filename="$APP_NAME" \
  "${FOLLOW_FLAGS[@]}" \
  "${HEAVY_EXCLUDE_FLAGS[@]}" \
  "${INCLUDE_FLAGS[@]}" \
  "${DATA_FILE_FLAGS[@]}" \
  --nofollow-import-to="$EXCLUDE_STDLIB" \
  --python-flag=no_asserts,no_docstrings \
  --lto=no \
  --disable-cache=ccache \
  --assume-yes-for-downloads \
  --jobs="$(nproc)"

log_ok "Nuitka compilation finished: $OUTPUT_DIR/main.dist/"
log_info "Proceeding to AppImage creation..."
bash build-appdir.sh