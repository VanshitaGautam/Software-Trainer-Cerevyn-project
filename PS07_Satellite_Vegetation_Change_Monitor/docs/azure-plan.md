# Azure deployment plan — PS07

## Proposed architecture
- **Compute:** Azure App Service for Linux running the container image. A small Linux App Service plan is sufficient for a prototype; select the lowest supported tier after checking current regional pricing and assessment constraints.
- **Container registry:** Azure Container Registry (optional for a simple deployment; a public GitHub Container Registry image is another option).
- **Input/output storage:** Azure Blob Storage if scenes and exports need persistence. The current prototype uses browser upload and downloadable files and does not require a cloud account.
- **Identity:** Prefer a managed identity for Blob Storage access. Grant only the minimum required data-plane role.
- **Secrets:** No secrets are needed for the local sample. If storage is added, keep connection strings out of source control; use App Service settings or Key Vault references.
- **Monitoring:** Application Insights / Azure Monitor for errors, startup failures, request latency and dependency failures. Do not log uploaded sensitive data.
- **CI:** GitHub Actions runs unit tests on pushes and pull requests. A separate manual deployment workflow can build/push the image and deploy after repository secrets and Azure OIDC federation are configured.

## Deployment outline
1. Create an Azure resource group in the selected region.
2. Build the Docker image and push it to a registry.
3. Create Linux App Service for Containers and configure the image and port `8501`.
4. Configure health/startup behavior and non-secret application settings.
5. If Blob Storage is integrated, enable managed identity and assign least-privilege access.
6. Configure HTTPS, logging and budget alerts.
7. Test the deployed dashboard with the included synthetic scene and verify exports.
8. Tear down resources after assessment if no longer needed.

## Cost and security assumptions
- Live deployment is optional. Local execution is the expected baseline.
- Do not create paid resources until necessary. Confirm current pricing for the chosen region and tier.
- Never commit credentials, access keys, personal data or real farm data.
- Limit upload size and validate array dimensions if accepting untrusted uploads in a hosted environment.
- Add authentication before using the service with non-public data.

## Current limitations
The included app does not connect to Azure or persist uploads. This document is an implementation plan, not evidence of a deployed service.
