FROM python:3.12-alpine3.20

# Set one or more individual labels
# LABEL com.example.version="0.0.1-beta"
# LABEL vendor1="ACME Incorporated"
# LABEL vendor2=ZENITH\ Incorporated
# LABEL com.example.release-date="2015-02-12"
# LABEL com.example.version.is-production=""

WORKDIR /usr/local/budapestmetrodisplay

# Install build dependencies only for i386 platform
RUN --platform=$BUILDPLATFORM \
    if [ "$BUILDPLATFORM" = "linux/arm/v7" ]; then \
        apk add --no-cache cmake ninja; \
    elif [ "$BUILDPLATFORM" = "linux/i386" ]; then \
        apk add --no-cache gcc g++ musl-dev libc-dev cargo; \
    fi

# Install the application
RUN pip install --no-cache-dir BudapestMetroDisplay

# sACN port
EXPOSE 5568

# Setup an app user so the container doesn't run as the root user
RUN adduser -D app
USER app

CMD ["BudapestMetroDisplay"]