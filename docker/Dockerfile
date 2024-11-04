FROM --platform=$BUILDPLATFORM python:3.12-alpine3.20
ARG $app_version 0.2.0

# Add build arguments for specific architectures
ARG TARGETPLATFORM

LABEL org.opencontainers.image.url=https://github.com/denes44/BudapestMetroDisplay
LABEL org.opencontainers.image.documentation=https://github.com/denes44/BudapestMetroDisplay/blob/main/docker/README.md
LABEL org.opencontainers.image.source=https://github.com/denes44/BudapestMetroDisplay/tree/main/software/src/BudapestMetroDisplay
LABEL org.opencontainers.image.authors=denes44
LABEL org.opencontainers.image.title=BudapestMetroDisplay
LABEL org.opencontainers.image.description=Backgorund service for a BudapestMetroDisplay hardware LED display
LABEL org.opencontainers.image.version=$app_version

WORKDIR /usr/local/budapestmetrodisplay

# Install build dependencies only for i386 platform
RUN \
    if [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then \
        apk add --no-cache cmake ninja; \
    elif [ "$TARGETPLATFORM" = "linux/i386" ]; then \
        apk add --no-cache gcc g++ musl-dev libc-dev cargo; \
    fi

# Install the application
RUN pip install --no-cache-dir BudapestMetroDisplay==$app_version

# sACN port
EXPOSE 5568

# Setup an app user so the container doesn't run as the root user
RUN adduser -D app
USER app

CMD ["BudapestMetroDisplay"]