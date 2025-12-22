# Custom Odoo 18.0 with OCA Modules
# Extends official odoo:18.0 image with Python dependencies and custom addons
# Build from odoo directory: docker build -t safee-odoo:18.0 .

FROM odoo:18.0

USER root

# Install gettext-base for envsubst command (environment variable substitution)
RUN apt-get update && apt-get install -y gettext-base && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for OCA modules
COPY odoo/requirements.txt /tmp/odoo-requirements.txt
RUN pip3 install --break-system-packages --ignore-installed typing-extensions -r /tmp/odoo-requirements.txt \
    && rm /tmp/odoo-requirements.txt

# Copy custom addons (138 OCA modules + 2 custom modules)
# These will be mounted at /mnt/extra-addons which Odoo scans by default
COPY odoo/custom_addons /mnt/extra-addons/
RUN chown -R odoo:odoo /mnt/extra-addons

# Switch back to odoo user for security
USER odoo

# Ensure odoo user owns the /var/lib/odoo directory
RUN chown -R odoo:odoo /var/lib/odoo

# Expose Odoo web interface
EXPOSE 8069

# Copy Odoo configuration file
COPY odoo/odoo.conf /etc/odoo/odoo.conf.template

# Default command (can be overridden for init operations)
COPY odoo/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY scripts/init-odoo-template.sh /usr/local/bin/init-odoo-template.sh
USER root
RUN chmod +x /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/init-odoo-template.sh
USER odoo

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]

