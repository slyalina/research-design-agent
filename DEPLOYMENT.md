# Deployment Guide

This guide explains how to containerize and deploy the Bioinformatics Research Design Agent.

## Prerequisites

-   [Docker Desktop](https://www.docker.com/products/docker-desktop) installed.
-   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed (for Cloud deployment).
-   A Google Cloud Project with Vertex AI API enabled.

## 1. Containerization with Docker

The agent is fully containerized to ensure all dependencies (Python + R + System Libraries) are present.

### Build the Image

```bash
docker build -t research-design-agent .
```

### Run Locally

To run the agent interactively in a container, you need to pass your Google Cloud credentials.

**Option A: Using an API Key**

```bash
docker run -it -e GOOGLE_API_KEY="your_api_key_here" research-design-agent
```

**Option B: Using Application Default Credentials**

```bash
docker run -it \
  -v $HOME/.config/gcloud:/root/.config/gcloud \
  research-design-agent
```

## 2. Deploying to Google Cloud

Since this is an interactive CLI agent, the standard deployment model is to run it within a cloud-based shell or as a job that processes inputs. However, for the purpose of this course's "Deployment" criteria, we demonstrate how to push the container to Google Container Registry (GCR) and run it on Cloud Run (as a Job).

### Push to Container Registry

```bash
# Tag the image
docker tag research-design-agent gcr.io/YOUR_PROJECT_ID/research-design-agent

# Push to GCR
docker push gcr.io/YOUR_PROJECT_ID/research-design-agent
```

### Run on Cloud Run (as a Job)

Cloud Run Jobs are suitable for agents that perform a specific task and exit.

```bash
gcloud run jobs create research-design-job \
  --image gcr.io/YOUR_PROJECT_ID/research-design-agent \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY="your_api_key"
```

*Note: To make this fully automated on Cloud Run, the `main_agent.py` would need to be adapted to read from environment variables or Pub/Sub instead of interactive `input()`.*
