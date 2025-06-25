# Use the official Python 3.11 image as a base
FROM python:3.11-bullseye

# Set up a working directory
WORKDIR /workspace

# Copy the entire workspace
COPY .. /workspace

# Install system dependencies if packages.txt exists
RUN if [ -f packages.txt ]; then \
      apt-get update && \
      apt-get upgrade -y && \
      xargs apt-get install -y < packages.txt; \
    fi

# Install Python dependencies with retry logic
RUN if [ -f requirements.txt ]; then \
      pip install --no-cache-dir --retries 3 --timeout 60 -r requirements.txt; \
    fi

# Always install streamlit with retry logic
RUN pip install --no-cache-dir --retries 3 --timeout 60 streamlit

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1

# Expose the default Streamlit port
EXPOSE 8501

# Default command (can be overridden by postAttachCommand)
CMD ["bash"] 