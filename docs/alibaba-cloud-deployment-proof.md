# Alibaba Cloud Deployment Proof Plan

## Current Billing Position

We will not use pay-as-you-go resources before Qwen Cloud hackathon credits are activated.

The coupon request has been submitted and is under registration verification.

## Planned Deployment

Backend target:

- Alibaba Cloud ECS
- Docker Compose
- FastAPI backend on port 8000

## Deployment Files

- backend/Dockerfile
- infra/alibaba/docker-compose.prod.yml
- backend/app/services/qwen_client.py

## Proof Video Checklist

The proof video should show:

1. Alibaba Cloud ECS instance running.
2. SSH connection into the instance.
3. Repository cloned.
4. Docker Compose backend startup.
5. Healthcheck:

curl http://PUBLIC_ECS_IP:8000/health

Expected result:

{
  "status": "ok",
  "service": "OpsPilot Backend",
  "mock_llm": true
}

6. Incident workflow call.
7. Vercel environment variable updated:

NEXT_PUBLIC_API_BASE_URL=http://PUBLIC_ECS_IP:8000

8. Live Vercel frontend calling Alibaba Cloud backend.

## Real Qwen Mode

After credits are activated:

USE_MOCK_LLM=false
FALLBACK_TO_MOCK_ON_ERROR=true
QWEN_API_BASE=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=<activated_key>
QWEN_MODEL=qwen-plus
