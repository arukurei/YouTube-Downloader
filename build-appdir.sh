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
OUTPUT_DIR="dist"
ICON_PATH="assets/icon.png"
APPIMAGETOOL="$HOME/Софт/appimagetool-x86_64.AppImage"
APP_KIND="tui"

APPDIR="${APP_NAME}.AppDir"
DIST_SRC="$OUTPUT_DIR/main.dist"

if [ ! -d "$DIST_SRC" ]; then
  log_err "Directory '$DIST_SRC' not found. Run compile.sh first."
  exit 1
fi

log_step "Assembling AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
cp -r "$DIST_SRC"/* "$APPDIR/usr/bin/"
cp "$ICON_PATH" "$APPDIR/icon.png"
log_info "Files copied to $APPDIR"

if [ -f "$APPDIR/usr/bin/ffmpeg" ]; then
  log_ok "ffmpeg found inside build"
else
  log_warn "ffmpeg not found in $APPDIR/usr/bin/"
fi

log_info "Generating desktop file..."
cat > "$APPDIR/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=${APP_NAME}
Exec=${APP_NAME}
Icon=icon
Categories=Utility;
Terminal=false
EOF

log_info "Generating AppRun entrypoint..."
if [ "$APP_KIND" = "tui" ]; then
  cat > "$APPDIR/AppRun" <<EOF
#!/usr/bin/env bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"
BIN="\$HERE/usr/bin/${APP_NAME}"

if [ -t 1 ]; then
  exec "\$BIN" "\$@"
fi

for term in x-terminal-emulator gnome-terminal konsole xfce4-terminal xterm; do
  if command -v "\$term" >/dev/null 2>&1; then
    case "\$term" in
      gnome-terminal) exec "\$term" -- "\$BIN" "\$@" ;;
      konsole)        exec "\$term" -e "\$BIN" "\$@" ;;
      xfce4-terminal)  exec "\$term" -e "\$BIN \$*" ;;
      *)               exec "\$term" -e "\$BIN" "\$@" ;;
    esac
  fi
done

echo "No terminal emulator found. Run the binary manually from a terminal." >&2
exit 1
EOF
else
  cat > "$APPDIR/AppRun" <<EOF
#!/usr/bin/env bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"
exec "\$HERE/usr/bin/${APP_NAME}" "\$@"
EOF
fi
chmod +x "$APPDIR/AppRun"
chmod +x "$APPDIR/usr/bin/${APP_NAME}"

if [ ! -f "$APPIMAGETOOL" ]; then
  log_err "appimagetool not found at: $APPIMAGETOOL"
  log_notice "Download it with:"
  echo "  wget -O \"$APPIMAGETOOL\" https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
  exit 1
fi

log_step "Building AppImage"
ARCH=x86_64 "$APPIMAGETOOL" "$APPDIR" "${APP_NAME}-x86_64.AppImage"
chmod +x "${APP_NAME}-x86_64.AppImage"

log_ok "Build complete: ${C_BOLD}${APP_NAME}-x86_64.AppImage${C_RESET}"
