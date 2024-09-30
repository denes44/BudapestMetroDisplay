#!/usr/bin/env bash
source <(curl -s https://raw.githubusercontent.com/denes44/BudapestMetroDisplay/main/software/proxmox/misc/build.func)
# Copyright (c) 2024 denes44
# Copyright (c) 2021-2024 tteck
# Author: denes44, tteck
# License: MIT
# https://github.com/denes44/BudapestMetroDisplay/raw/main/software/LICENSE
# https://github.com/tteck/Proxmox/raw/main/LICENSE

function header_info {
clear
cat <<"EOF"
    ____            __                      __  __  ___     __             ____  _            __           
   / __ )__  ______/ /___ _____  ___  _____/ /_/  |/  /__  / /__________  / __ \(_)________  / /___ ___  __
  / __  / / / / __  / __ `/ __ \/ _ \/ ___/ __/ /|_/ / _ \/ __/ ___/ __ \/ / / / / ___/ __ \/ / __ `/ / / /
 / /_/ / /_/ / /_/ / /_/ / /_/ /  __(__  ) /_/ /  / /  __/ /_/ /  / /_/ / /_/ / (__  ) /_/ / / /_/ / /_/ / 
/_____/\__,_/\__,_/\__,_/ .___/\___/____/\__/_/  /_/\___/\__/_/   \____/_____/_/____/ .___/_/\__,_/\__, /  
                       /_/                                                         /_/            /____/   
EOF
}
header_info
echo -e "Loading..."
APP="BudapestMetroDisplay"
var_disk="2"
var_cpu="2"
var_ram="512"
var_os="debian"
var_version="12"
variables
color
catch_errors

function default_settings() {
  CT_TYPE="1"
  PW=""
  CT_ID=$NEXTID
  HN=$NSAPP
  DISK_SIZE="$var_disk"
  CORE_COUNT="$var_cpu"
  RAM_SIZE="$var_ram"
  BRG="vmbr0"
  NET="dhcp"
  GATE=""
  APT_CACHER=""
  APT_CACHER_IP=""
  DISABLEIP6="no"
  MTU=""
  SD=""
  NS=""
  MAC=""
  VLAN=""
  SSH="no"
  VERB="no"
  echo_default
}

function update_script() {
header_info
if [[ ! -d /var ]]; then msg_error "No ${APP} Installation Found!"; exit; fi
msg_info "Updating $APP LXC"
apt-get update &>/dev/null
apt-get -y upgrade &>/dev/null
msg_ok "Updated $APP LXC"
exit
}

start
build_container
description

msg_ok "Completed Successfully!\n"
