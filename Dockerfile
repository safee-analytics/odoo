# Custom Odoo 18.0 with OCA Modules
# Extends official odoo:18.0 image with Python dependencies and custom addons
# Build from project root: docker build -f odoo/Dockerfile -t safee-odoo:18.0 .

FROM odoo:18.0

USER root

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

# Expose Odoo web interface
EXPOSE 8069

# Default command (can be overridden for init operations)
CMD ["odoo"]
