#!/usr/bin/with-contenv bashio

# Set location for logs
mkdir -p /config/logs
export LOG_PATH="/config/logs/"

# Change working directory
cd /opt/BudapestMetroDisplay/

# Initialize command
COMMAND="/opt/BudapestMetroDisplay/.venv/bin/BudapestMetroDisplay"

# Get the log level from the configuration
APP_LOG_LEVEL=$(bashio::config 'APP_LOG_LEVEL')

if [[ "$APP_LOG_LEVEL" == "trace" ]]; then
    exec $COMMAND --trace
elif [[ "$APP_LOG_LEVEL" == "debug" ]]; then
    exec $COMMAND --debug
else
    exec $COMMAND  # Run without additional options
fi
