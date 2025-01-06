#!/usr/bin/env bash

# Copyright (c) 2024 denes44
# Copyright (c) 2021-2024 tteck
# Author: denes44, tteck
# License: MIT
# https://github.com/denes44/BudapestMetroDisplay/raw/main/proxmox-script/LICENSE
# https://github.com/tteck/Proxmox/raw/main/LICENSE

source /dev/stdin <<< "$FUNCTIONS_FILE_PATH"
color
verb_ip6
catch_errors
setting_up_container
network_check
update_os

msg_info "Installing Dependencies"
$STD apt-get install -y curl
$STD apt-get install -y sudo
$STD apt-get install -y mc
msg_ok "Installed Dependencies"

msg_info "Updating Python3"
$STD apt-get install -y \
  python3 \
  python3-dev \
  python3-pip \
  python3-venv
rm -rf /usr/lib/python3.*/EXTERNALLY-MANAGED
msg_ok "Updated Python3"

msg_info "Installing BudapestMetroDisplay"
mkdir -p /opt/BudapestMetroDisplay
cd /opt/BudapestMetroDisplay
python3 -m venv .venv > /dev/null 2>&1
source .venv/bin/activate
python3 -m pip install -q BudapestMetroDisplay > /dev/null 2>&1
deactivate
wget -qL https://raw.githubusercontent.com/denes44/BudapestMetroDisplay/refs/heads/main/software/src/BudapestMetroDisplay/.env.sample -O .env
touch .env
msg_ok "Installed BudapestMetroDisplay"

msg_info "Creating Service"
cat <<EOF >/etc/systemd/system/BudapestMetroDisplay.service
[Unit]
# service description
Description=BudapestMetroDisplay
After=network.target

[Service]
Type=simple

# user and group -- to run service
User=root
Group=root

# project working directory
WorkingDirectory=/opt/BudapestMetroDisplay

# File containing the environmental values
EnvironmentFile=/opt/BudapestMetroDisplay/.env

# Command to execute when the service is started
ExecStart=/opt/BudapestMetroDisplay/.venv/bin/BudapestMetroDisplay

# Automatically restart the service if it crashes
Restart=always

[Install]
# Tell systemd to automatically start this service when the system boots
# (assuming the service is enabled)
WantedBy=multi-user.target
EOF
systemctl enable -q --now BudapestMetroDisplay
msg_ok "Created Service"

motd_ssh
customize

msg_info "Cleaning up"
$STD apt-get -y autoremove
$STD apt-get -y autoclean
msg_ok "Cleaned"
