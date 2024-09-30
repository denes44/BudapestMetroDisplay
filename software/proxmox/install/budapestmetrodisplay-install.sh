#!/usr/bin/env bash

# Copyright (c) 2024 denes44
# Copyright (c) 2021-2024 tteck
# Author: denes44, tteck
# License: MIT
# https://github.com/denes44/BudapestMetroDisplay/raw/main/software/LICENSE
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
  python3-pip
rm -rf /usr/lib/python3.*/EXTERNALLY-MANAGED
msg_ok "Updated Python3"

msg_info "Installing BudapestMetroDisplay"

msg_ok "Installed BudapestMetroDisplay"

msg_info "Creating Service"

msg_ok "Created Service"

motd_ssh
customize

msg_info "Cleaning up"
$STD apt-get -y autoremove
$STD apt-get -y autoclean
msg_ok "Cleaned"