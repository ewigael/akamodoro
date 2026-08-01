#!/usr/bin/env bash
set -euo pipefail

pip install -e .

mkdir -p "$HOME/.config/systemd/user"

stow --verbose --target="$HOME" systemd

systemctl --user daemon-reload
systemctl --user enable --now akamodoro.service