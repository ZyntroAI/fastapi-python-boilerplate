# Chrome DevTools MCP server — container image.
#
# Pin by digest in production, not by tag:
#   FROM node:20.19-alpine@sha256:<digest>
#
# Chromium is installed from Alpine's *community* repository. A bare
# `node:20.19-alpine` image enables main and community, so no extra repo
# configuration is needed here; if you build on a base that only enables main,
# add the community repo explicitly.
FROM node:20.19-alpine

# Chromium (itself from the community repo) plus the fonts and runtime libs it
# needs to launch in headless mode. All debug ports stay inside the container.
RUN apk add --no-cache \
        chromium \
        nss \
        freetype \
        harfbuzz \
        ca-certificates \
        ttf-freefont \
        jq \
    && rm -rf /var/cache/apk/*

# The MCP server owns the browser it launches; point it at the packaged binary
# rather than letting Puppeteer download its own copy.
ENV CHROME_PATH=/usr/bin/chromium-browser \
    CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS=1 \
    NODE_ENV=production

WORKDIR /app

# Only the config is baked in. The server itself is fetched at run time by the
# pinned spec below, so the image does not need an npm install step.
COPY mcp-config.json /app/mcp-config.json

# Run as the non-root user that the node base image already provides.
USER node

# Warm the package into the image layer so the first tool call is not blocked on
# a network fetch. Version here MUST match the spec in mcp-config.json.
RUN npx -y chrome-devtools-mcp@1.4.0 --help > /dev/null

# The MCP server speaks JSON-RPC over stdio. It is not a network service and
# exposes no port -- there is deliberately no EXPOSE line.
#
# Note: there is no `--config` flag. The client reads mcp-config.json and passes
# these arguments to the server, so they are spelled out here directly. Keep this
# list identical to the args in mcp-config.json -- `verify-mcp-flags.py` checks both.
ENTRYPOINT ["npx", "-y", "chrome-devtools-mcp@1.4.0", \
            "--headless", \
            "--isolated", \
            "--redact-network-headers", \
            "--no-usage-statistics", \
            "--no-performance-crux", \
            "--channel=stable", \
            "--user-data-dir=/tmp/chrome-mcp-profile", \
            "--log-file=/var/log/chrome-devtools-mcp.log", \
            "--blocked-url-pattern=https://*/auth/*", \
            "--blocked-url-pattern=https://*/api/*/private"]
