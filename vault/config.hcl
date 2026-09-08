# FastAPI Service — Vault policy (least privilege, read-only)
path "secret/data/fastapi/*" {
  capabilities = ["read"]
}
path "secret/data/broker/fastapi" {
  capabilities = ["read"]
}
path "secret/data/github/workflow" {
  capabilities = ["read"]
}
path "identity/oidc/token/fastapi" {
  capabilities = ["create", "read"]
}
path "sys/leases/lookup" {
  capabilities = ["read"]
}
