# Security and clinical safety

Do not submit real identifiable patient information. The prototype lacks authentication, deployment hardening and clinical validation; operate locally for evaluation. The research API sends **condition and query text** to Europe PMC, and optional AI mode sends topic/evidence text to a configured model provider. Never place names, IDs, contact details, sensitive record fragments or secrets in those fields.

Do not use this prototype as an autonomous diagnosis, prescription, dosing, triage, interaction-checking or treatment execution system. Published papers and LLM summaries are not automatically approved guidelines. Clinical-mode metadata alone does not prove clinical eligibility has been checked.

For vulnerabilities, please contact repository maintainers privately rather than including exploit details or secrets in public issues.

## Model routing

Local inference via Ollama/LM Studio keeps research prompts on the local model server. Literature search still sends de-identified queries to remote sources after consent. Cloud inference requires `CLINOR_ALLOW_CLOUD_LLM=1` **and** an explicit `consent_cloud_llm=true` on each content request. Provider URLs and keys are server-managed.

Do not expose the development FastAPI server, Ollama, or LM Studio endpoint to an untrusted network. LLM output remains untrusted and source-ID inclusion does not prove a summary is factually supported by an article.
