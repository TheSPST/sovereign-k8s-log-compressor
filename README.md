# Sovereign K8s Log Compressor — DaemonSet Sidecar

A Kubernetes DaemonSet that runs on every node in your cluster, tails pod log streams, and compresses them on-the-fly via the Sovereign Cloud SPST Codec — reducing cluster log storage and egress costs by **80-95%**.

## Quick Deploy

```bash
# 1. Create the API key secret
kubectl create secret generic sovereign-credentials \
  --from-literal=api-key=YOUR_AWS_MARKETPLACE_KEY

# 2. Deploy the DaemonSet to every node
kubectl apply -f daemonset.yaml
```

## How It Works

1. Runs as a DaemonSet on every Kubernetes node
2. Monitors `/var/log/pods` for new log chunks
3. Streams log data to Sovereign Cloud API for compression
4. Compressed `.sov` files replace raw logs — 80-95% smaller
5. Metered billing via AWS Marketplace subscription

## Files

- `daemonset.yaml` — Kubernetes DaemonSet manifest
- `sidecar.py` — Python agent that tails and compresses logs

## Environment Variables

| Variable | Description |
|---|---|
| `SOVEREIGN_API_KEY` | Your AWS Marketplace API key (from secret) |
| `SOVEREIGN_API_URL` | `https://a3pme2hx4v.us-east-1.awsapprunner.com` |
| `LOG_DIR` | Pod log directory (default: `/var/log/pods`) |
