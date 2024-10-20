#!/usr/bin/with-contenv bashio

# Get the log level from the environment variable
APP_LOG_LEVEL=$(bashio::config 'APP_LOG_LEVEL')

# Force sACN output to unicast
SACN_MULTICAST=false

# Change working directory
cd /opt/BudapestMetroDisplay/

# Initialize command
COMMAND="/opt/BudapestMetroDisplay/.venv/bin/BudapestMetroDisplay"

# Check the log level and modify the command accordingly
if [[ "$APP_LOG_LEVEL" == "trace" ]]; then
    exec $COMMAND --trace
elif [[ "$APP_LOG_LEVEL" == "debug" ]]; then
    exec $COMMAND --debug
else
    exec $COMMAND  # Run without additional options
fi
