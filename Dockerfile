FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts during install
ENV DEBIAN_FRONTEND=noninteractive

# Install Java 21, git, unzip, wget, and other dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:openjdk-r/ppa && \
    apt-get update && \
    apt-get install -y \
        openjdk-21-jdk \
        git \
        unzip \
        wget \
        ca-certificates \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME and update PATH
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Set working directory
WORKDIR /opt

# Clone the RetroTector repository
RUN git clone https://github.com/MauricioMoldes/RetroTector.git

# Change into the repository directory
WORKDIR /opt/RetroTector

# Unzip the ReTe1.0.1.zip archive
RUN unzip ReTe1.0.1.zip

# Set working directory to the unzipped RetroTector folder
WORKDIR /opt/RetroTector/ReTe1.0.1

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make it executable
RUN chmod +x /entrypoint.sh

# Set the default command
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]


