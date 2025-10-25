# Odoo 19.0 with Custom REST API Module
FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build dependencies
    build-essential \
    libpq-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    # Runtime dependencies
    postgresql-client \
    git \
    curl \
    gosu \
    # wkhtmltopdf for PDF reports
    wkhtmltopdf \
    # Node.js for asset building
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create odoo user
RUN useradd -m -d /opt/odoo -s /bin/bash odoo

# Set working directory
WORKDIR /opt/odoo

# Copy Odoo source code (will be from the cloned repo)
COPY --chown=odoo:odoo . /opt/odoo

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir PyJWT

# Create directories for Odoo
RUN mkdir -p /var/lib/odoo \
    && chown -R odoo:odoo /var/lib/odoo

# Create config directory and copy configuration (it's already in /opt/odoo from line 39)
RUN mkdir -p /etc/odoo \
    && cp /opt/odoo/odoo.conf /etc/odoo/odoo.conf \
    && chmod +x /opt/odoo/entrypoint.sh \
    && cp /opt/odoo/entrypoint.sh /entrypoint.sh \
    && chown -R odoo:odoo /etc/odoo

# Expose Odoo port
EXPOSE 8069

# Set entrypoint (runs as root, switches to odoo user inside)
ENTRYPOINT ["/entrypoint.sh"]
CMD []
