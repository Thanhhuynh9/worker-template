FROM runpod/serverless:gpu-cuda12.1

# Install system dependencies for medical libraries
RUN apt update && apt install -y \
    python3 python3-pip \
    libgl1 libglib2.0-0 libnvinfer-dev libnvinfer-plugin-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy dependency list
COPY requirements.txt /requirements.txt

# Install Python packages
RUN pip install --no-cache-dir -r /requirements.txt

# Create workspace
RUN mkdir -p /workspace
COPY handler.py /handler.py

CMD ["python3", "/handler.py"]
