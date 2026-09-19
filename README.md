# LLM Automation Stack

> **Local-first hybrid LLM inference routing and quota exhaustion failover engine.**

```
                        ┌──────────────────────────────┐
                        │    QuotaManager.dispatch()   │
                        └──────────────┬───────────────┘
                                       │
                 ┌─────────────────────┼─────────────────────┐
                 │ (used < 14400)      │ (used < 5000)       │ (fallback)
                 ▼                     ▼                     ▼
          ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
          │    Groq     │       │  Replicate  │       │   Ollama    │
          │ (Fast Edge) │       │ (High Spec) │       │(Local ∞-Cap)│
          └─────────────┘       └─────────────┘       └─────────────┘
```

Single-provider LLM architectures are operational liabilities. When cloud rate limits trip or third-party APIs experience outages, monolithic agent pipelines fail silently.

`llm-automation-stack` establishes a resilient, dual-layer inference topology: high-throughput cloud providers (Groq, Replicate) handle bursts under explicit quota ceilings, with an automated fallback to local containerized Ollama inference ($quota = \infty$).

---

## ✦ Quota Routing Topology

The routing contract evaluates available quota pools deterministically:

```python
providers = {
    'ollama': {'quota': float('inf'), 'local': True},
    'groq': {'quota': 14400, 'used': 0},
    'replicate': {'quota': 5000, 'used': 0}
}

def get_available_provider() -> str:
    """Returns the primary cloud provider within quota limits; defaults to local Ollama."""
    for name, info in providers.items():
        if not info.get('local') and info['used'] < info['quota']:
            return name
    return 'ollama'  # Sovereign local floor
```

---

## ✦ Container Infrastructure

Packaged for immediate orchestration via Docker Compose with co-located prompt compression:

```yaml
version: '3.8'
services:
  ollama:
    image: ollama/ollama
    volumes:
      - ./models:/root/.ollama
    ports:
      - "11434:11434"
    restart: always

  llmlingua:
    build: .
    environment:
      - COMPRESSION_RATIO=25
      - FIDELITY=0.98
    depends_on:
      - ollama
```

---

## ✦ Operational Guarantees

1. **Zero Pipeline Stalls**: If upstream APIs encounter rate-limiting (HTTP 429) or connection timeouts, requests seamlessly transition to local models.
2. **Quota Transparency**: Provider exhaustion counters remain auditable at the network boundary.
3. **Data Sovereignty**: Sensitive workloads can enforce the `local: True` constraint, bypassing external network hops entirely.

---

## ✦ License
[MIT](LICENSE) © LERMF
