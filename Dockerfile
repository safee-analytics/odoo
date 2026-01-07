# Custom Odoo 18.0 with OCA Modules
# Extends official odoo:18.0 image with Python dependencies and custom addons
# Build from odoo directory: docker build -t safee-odoo:18.0 .

FROM odoo:18.0

USER root

# Install gettext-base for envsubst command (environment variable substitution)
RUN apt-get update && apt-get install -y gettext-base && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for OCA modules
COPY requirements.txt /tmp/odoo-requirements.txt
RUN pip3 install --break-system-packages --ignore-installed typing-extensions -r /tmp/odoo-requirements.txt \
    && rm /tmp/odoo-requirements.txt

# Copy custom addons (138 OCA modules + 2 custom modules)
# These will be mounted at /mnt/extra-addons which Odoo scans by default
COPY custom_addons /mnt/extra-addons/
RUN chown -R odoo:odoo /mnt/extra-addons

# Copy Odoo configuration file (as root before switching to odoo user)
# Try odoo.conf first (local builds), fall back to template (CI builds)
COPY odoo.conf* /tmp/
RUN if [ -f /tmp/odoo.conf ]; then \
      cp /tmp/odoo.conf /etc/odoo/odoo.conf.template; \
    else \
      cp /tmp/odoo.conf.template /etc/odoo/odoo.conf.template; \
    fi && rm -f /tmp/odoo.conf*

# Copy entrypoint scripts
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY init-odoo-template.sh /usr/local/bin/init-odoo-template.sh
RUN chmod +x /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/init-odoo-template.sh

# Switch to odoo user for security
USER odoo

# Expose Odoo web interface
EXPOSE 8069

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]

