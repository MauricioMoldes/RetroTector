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
```

## Run a Container for a Sample

```bash
docker run --rm -it \
  -v /path/to/sample1/:/opt/RetroTector/ReTe1.0.1/Workplace/ \
  -w /opt/RetroTector/ReTe1.0.1 \
  retrotector bash
```

## Run Multiple Containers with Docker Compose

We provide a `docker-compose.yml` example to run four instances in parallel, each mounted to a different sample directory.

```bash
docker-compose up --build
```

## Singularity Image

To deploy on HPC clusters, convert the Docker image to a Singularity image:

```bash
singularity build retrotector.sif docker-daemon://retrotector:latest
```


## Usage Notes

The configuration file `/opt/RetroTector/ReTe1.0.1/Database/Config.txt` is automatically updated in the container to set the correct working directory.

The container runs RetroTector commands:

```bash
java -cp RetroTector101.jar retrotector.RetroTectorEngine SweepDNA quit
java -cp RetroTector101.jar retrotector.RetroTectorEngine SweepScripts quit
```


Mount your input data to `/opt/RetroTector/ReTe1.0.1/Workplace/` inside the container.

## Contact & Contributions

For questions or contributions, please contact:

Department of Genomic Medicine  
Rigshospitalet, Copenhagen, Denmark  
Email: [frederik.otzen.bagger@regionh.dk]
