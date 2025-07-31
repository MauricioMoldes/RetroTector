# RetroTector - Fork by Department of Genomic Medicine, Rigshospitalet

Welcome to our fork of **RetroTector**, a tool for detecting endogenous retroviruses in genomic sequences.

---

## About This Fork

This repository contains our customized version of RetroTector maintained by the Department of Genomic Medicine, Rigshospitalet, Denmark. We have enhanced the original application by creating a **Docker container** to simplify deployment and usage across various computing environments, including HPC clusters.

Our goal is to ensure the software is robust, reproducible, and easy to integrate into modern bioinformatics pipelines.

---

## Features

- **Containerized Application:**  
  We provide a Docker image that packages RetroTector and all its dependencies, including Java 21, ensuring consistent execution regardless of the host system.

- **Parallel Execution:**  
  Our Docker Compose setup supports running multiple instances concurrently with separate mounted workspaces.

- **Configuration Automation:**  
  The container entrypoint automatically updates configuration files to reflect the runtime environment, enabling seamless operation without manual tweaks.

- **Cluster Ready:**  
  The container is designed to be compatible with HPC environments and can be converted to Singularity images for cluster deployment.

---

## Quick Start

### Build the Docker Image

```bash
docker build -t retrotector .

