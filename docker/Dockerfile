FROM python:3.12-alpine3.20

# Set one or more individual labels
# LABEL com.example.version="0.0.1-beta"
# LABEL vendor1="ACME Incorporated"
# LABEL vendor2=ZENITH\ Incorporated
# LABEL com.example.release-date="2015-02-12"
# LABEL com.example.version.is-production=""

WORKDIR /usr/local/budapestmetrodisplay

# Install the application
RUN pip install --no-cache-dir BudapestMetroDisplay

# sACN port
EXPOSE 5568

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

CMD ["BudapestMetroDisplay"]