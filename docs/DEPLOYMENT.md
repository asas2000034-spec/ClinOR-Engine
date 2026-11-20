# Developer deployment notes

This app is a research prototype **without authentication, patient-data safeguards, rate limiting or authorization**. Run locally or inside a trusted development environment; do not expose an instance on the public Internet and do not send PHI to it.

## Local

```bash
python -m pip install -e '.[dev,ai,cp]'
uvicorn clinor.api:app --reload
```

The wheel includes UI assets from `clinor/static`. The editable checkout is not required for the packaged API homepage.

## Docker — offline solver showcase only

```bash
docker build -t clinor:0.2.0 .
docker run --rm -p 127.0.0.1:8000:8000 clinor:0.2.0
```

The basic Docker image does not install optional AI/CP-SAT extras and has no secrets. Europe PMC evidence discovery requires the container to have network access and opt-in on each request. For development-only optional services, inject environment variables securely; never bake keys into an image.

## Cloud/clinical rollout is intentionally unsupported

Before real-world clinical deployment, a separate project must add authorization, authentication, secret management, privacy threat modeling, encryption, rate controls, structured audit trails, external evaluation and regulatory review. The metadata guideline review gate does not authenticate a reviewer.
