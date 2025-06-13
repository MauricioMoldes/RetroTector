
FROM openjdk:8-jdk-slim

# Install dependencies
RUN apt-get update && apt-get install -y git ant && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /opt

# Clone RetroTector
RUN git clone https://github.com/PatricJernLab/RetroTector.git

# Build the .jar using Ant
WORKDIR /opt/RetroTector
RUN ant

# Copy wrapper script
COPY run_retro.sh /usr/local/bin/run_retro.sh
RUN chmod +x /usr/local/bin/run_retro.sh

# Set default entrypoint
ENTRYPOINT ["run_retro.sh"]


