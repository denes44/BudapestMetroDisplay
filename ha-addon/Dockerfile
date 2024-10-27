ARG BUILD_FROM
FROM $BUILD_FROM

# Execute during the build of the image
ARG APP_VERSION

RUN \
  mkdir -p /opt/BudapestMetroDisplay \
  && cd /opt/BudapestMetroDisplay \
  && python3 -m venv .venv \
  && source .venv/bin/activate \
  && python3 -m pip install -q BudapestMetroDisplay==${APP_VERSION} \
  && deactivate

# Copy your start script
COPY start.sh /opt/BudapestMetroDisplay/start.sh
RUN chmod a+x /opt/BudapestMetroDisplay/start.sh

# Command to run the entry point script
CMD ["/opt/BudapestMetroDisplay/start.sh"]
