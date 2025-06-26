# Use the official Python 3.11 image as a base
FROM python:3.11-bullseye

# Set up a working directory
WORKDIR /workspace

# Copy requirements.txt first for better caching
COPY ../requirements.txt /workspace/

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the workspace
COPY .. /workspace/

# Always install streamlit (in case it's not in requirements.txt)
RUN pip install streamlit

RUN mkdir -p ~/.streamlit/
RUN echo "[general]"  > ~/.streamlit/credentials.toml
RUN echo "email = \"\""  >> ~/.streamlit/credentials.toml

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]