# Odoo 19.0 with Custom REST API Module
FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
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
    postgresql-client \
    git \
    curl \
    gosu \
    wkhtmltopdf \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create odoo user
RUN useradd -m -d /opt/odoo -s /bin/bash odoo

WORKDIR /opt/odoo

COPY --chown=odoo:odoo . /opt/odoo

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir PyJWT

RUN mkdir -p /var/lib/odoo \
    && chown -R odoo:odoo /var/lib/odoo

RUN mkdir -p /etc/odoo \
    && cp /opt/odoo/odoo.conf /etc/odoo/odoo.conf \
    && chmod +x /opt/odoo/entrypoint.sh \
    && cp /opt/odoo/entrypoint.sh /entrypoint.sh \
    && chown -R odoo:odoo /etc/odoo

EXPOSE 8069

ENTRYPOINT ["/entrypoint.sh"]
CMD []
