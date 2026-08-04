#!/usr/bin/env bash
# APEX Local Toolchain Auto-Installer Script
# Installs native Termux/Linux compiler toolchains for maximum local execution

set -e

echo "=== APEX Toolchain Auto-Installer ==="

if command -v pkg >/dev/null 2>&1; then
    echo "[+] Termux environment detected. Updating package index..."
    pkg update -y || true
    echo "[+] Installing native compiler toolchains..."
    pkg install -y clang rust python elixir iverilog ghc || true
elif command -v apt-get >/dev/null 2>&1; then
    echo "[+] Debian/Ubuntu environment detected. Updating apt..."
    sudo apt-get update -y || true
    echo "[+] Installing build toolchains..."
    sudo apt-get install -y build-essential clang rustc python3 elixir iverilog ghc || true
fi

echo "=== Toolchain Auto-Installer Complete ==="
