# Use the official n8n image as the base
FROM docker.n8n.io/n8nio/n8n

# Set environment variables
# IMPORTANT: Replace <YOUR_TIMEZONE> with an actual value (e.g., "America/New_York")
ENV GENERIC_TIMEZONE="America_Sao_Paulo"
ENV TZ="America_Sao_Paulo"
ENV N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
ENV N8N_RUNNERS_ENABLED=true

# Expose the port n8n runs on (this is mostly for documentation)
EXPOSE 5678

# Define the volume for persistent data
VOLUME /home/node/.n8n