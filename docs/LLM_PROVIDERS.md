# LLM Providers and Privacy (v0.3.0)

ClinOR can run against an **entirely local LLM** or an **explicitly permitted cloud LLM**. No model is bundled or downloaded automatically. The model generates research queries and provisional evidence briefs, and can explain rule-based operations-research method suggestions. It **never modifies OR constraints, inserts medication scores, or authorizes treatment**.

## Quickest local path: Ollama

1. Install [Ollama](https://ollama.com/) separately.
2. Pull a small instruct model, for example:

   ```bash
   ollama pull qwen2.5:3b
   ollama serve # only if Ollama is not already running in the background
   ```

3. In this project:

   ```bash
   cp .env.example .env
   pip install -e '.[dev]'
   uvicorn clinor.api:app --reload
   ```

4. Open http://127.0.0.1:8000, click **Test model**, then run research with AI assistance. You must consent separately to external literature discovery (Europe PMC), but **no cloud inference is required**.

The default `qwen2.5:3b` is a practical starting point on moderate hardware. If memory permits, you can choose a stronger instruct model by setting `CLINOR_LLM_MODEL` to the name installed in Ollama. Larger models are not automatically better for grounded clinical tasks. Model quality needs evaluation.

## Local path: LM Studio / llama.cpp / vLLM

Start an OpenAI-compatible local server and load a JSON-capable instruct model. LM Studio often serves at http://127.0.0.1:1234/v1. In `.env` set:

```dotenv
CLINOR_LLM_PROVIDER=openai_compatible
CLINOR_LLM_DEPLOYMENT=local
CLINOR_LLM_MODEL=<model-id-shown-by-your-server>
CLINOR_LLM_BASE_URL=http://127.0.0.1:1234/v1
```

The adapter uses `/chat/completions` and normally requests `response_format=json_object`. If an older local provider rejects JSON mode, set `CLINOR_LLM_JSON_MODE=prompt_only` and use a model that reliably follows JSON instructions. Responses are still parsed and rejected if malformed.

## Cloud OpenAI-compatible API

Only when cloud inference is desired, set:

```dotenv
CLINOR_LLM_PROVIDER=openai_compatible
CLINOR_LLM_DEPLOYMENT=cloud
CLINOR_LLM_MODEL=<cloud-model-id>
CLINOR_LLM_BASE_URL=https://api.openai.com/v1
CLINOR_LLM_API_KEY=<private-key>
CLINOR_ALLOW_CLOUD_LLM=1
```

The server refuses to contact the cloud model unless the server-side opt-in exists. **Every research or method-advice request also requires separate `consent_cloud_llm=true`.** Never put credentials in the browser or commit `.env`.

## Docker Compose (local Ollama + ClinOR)

```bash
docker compose -f docker-compose.ollama.yml up -d --build
docker compose -f docker-compose.ollama.yml exec ollama ollama pull qwen2.5:3b
```

Open http://127.0.0.1:8000. Docker runs the model in an internal service named `ollama`; the app only publishes its own localhost web port. GPU passthrough is not configured by default. CPU inference may be slower.

## What is local, what still needs the internet?

- **Local:** language-model query planning, provisional evidence synthesis, OR method explanation, all mathematical OR computations.
- **External by default:** Europe PMC literature search; optional Brave publisher-web search. These services receive only the search topic/query, after consent.
- **Cloud LLM:** disabled unless deliberately configured on the server and consented to in each request.
- **Fully offline clinical research:** not yet supported. It requires a separately licensed and maintained local publication/guideline corpus and retrieval index.

## Data and trust boundaries

- Research topic and question must be de-identified; there is **no patient-data intake or privacy certification**.
- Abstracts and remote source text are untrusted input. LLM outputs must be checked; unsupported source IDs are discarded. The model can still misrepresent a real source; IDs alone are not factual verification.
- Only a domain-expert-maintained, versioned clinical rule pack can define clinical eligibility and hard treatment constraints. The current system does not provide such a validated pack.
- Arbitrary model endpoints cannot be submitted via API calls. Local server hostnames are allowlisted; additional private LAN hosts can be explicitly configured using `CLINOR_LLM_TRUSTED_HOSTS`.
- `/api/llm/status` exposes provider metadata without secrets. `/api/llm/check` performs an actual small model call and may consume cloud tokens if cloud is configured.
- Standard API errors conceal detailed provider response bodies, reducing accidental leakage of source or credential details.

## REST routes

| Route | Use |
|---|---|
| `GET /api/llm/status` | Inspect configured provider/model (no network) |
| `POST /api/llm/check` | Verify inference is reachable |
| `POST /api/research` | LLM planning, evidence retrieval and grounded provisional synthesis |
| `POST /api/llm/method-advice` | LLM explanation of deterministic OR candidates |
| `POST /api/or/recommend` | Offline deterministic OR technique suggestion (no LLM) |

The user-facing interface exposes these controls; no prompt or client-supplied URL is allowed to bypass consent.
