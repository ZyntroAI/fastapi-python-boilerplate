# 📋 Kubernetes Manifests — Deployment + Service + Config/Secrets
**Fully aligned** with your Dockerfile patterns: **runtime env injection**, `/health` endpoint healthcheck, non-root security, and image versioning. Works for **Next.js / Go / Rust** variants interchangeably.

---

## 📁 File Structure
```
k8s/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── secrets.example.yaml
└── overlays/
    ├── production/
    │   ├── kustomization.yaml
    │   └── config.env
    └── staging/
        ├── kustomization.yaml
        └── config.env
```

---

## 🧩 1. `deployment.yaml` — Core Workload
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
  labels:
    app.kubernetes.io/name: app
    app.kubernetes.io/version: latest
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: app
  template:
    metadata:
      labels:
        app.kubernetes.io/name: app
        app.kubernetes.io/version: latest
    spec:
      # 🔒 Security — match Dockerfile non-root user
      runAsNonRoot: true
      runAsUser: 1000
      runAsGroup: 1000
      fsGroup: 1000

      containers:
        - name: app
          image: ghcr.io/yourname/app:latest
          imagePullPolicy: IfNotPresent

          ports:
            - containerPort: 8080
              name: http
              protocol: TCP

          # ✅ Healthcheck — matches /health endpoint
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 30
            timeoutSeconds: 5
            failureThreshold: 3

          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3

          startupProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 2
            periodSeconds: 5
            failureThreshold: 12 # Allow 60s to start

          # 📦 Resource limits — prevent resource hogging
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 1000m
              memory: 512Mi

          # ✅ Runtime ENV injection — ConfigMap + Secrets
          env:
            # Public config from ConfigMap
            - name: API_BASE_URL
              valueFrom: { configMapKeyRef: { name: app-config, key: API_BASE_URL } }
            - name: ENVIRONMENT
              valueFrom: { configMapKeyRef: { name: app-config, key: ENVIRONMENT } }
            - name: APP_URL
              valueFrom: { configMapKeyRef: { name: app-config, key: APP_URL } }
            - name: TZ
              valueFrom: { configMapKeyRef: { name: app-config, key: TZ } }

            # Sensitive values from Secret — NEVER in ConfigMap
            - name: DATABASE_URL
              valueFrom: { secretKeyRef: { name: app-secrets, key: DATABASE_URL } }
            - name: NPM_TOKEN
              valueFrom: { secretKeyRef: { name: app-secrets, key: NPM_TOKEN, optional: true } }
            - name: GIT_AUTH_TOKEN
              valueFrom: { secretKeyRef: { name: app-secrets, key: GIT_AUTH_TOKEN, optional: true } }
            - name: API_SIGNING_KEY
              valueFrom: { secretKeyRef: { name: app-secrets, key: API_SIGNING_KEY, optional: true } }

          # Optional: Mount files (certs, config)
          volumeMounts: []

      imagePullSecrets:
        - name: ghcr-credentials
```

---

## 🧩 2. `service.yaml` — Internal Load Balancer
```yaml
apiVersion: v1
kind: Service
metadata:
  name: app
  labels:
    app.kubernetes.io/name: app
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: app
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
  # Session affinity None → load balance evenly across pods
  sessionAffinity: None
```

---

## 🧩 3. `configmap.yaml` — Public Runtime Config
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  # ✅ Non-sensitive config — injected at RUNTIME
  API_BASE_URL: "https://api.prod.yourdomain.com"
  APP_URL: "https://app.yourdomain.com"
  ENVIRONMENT: "production"
  TZ: "Asia/Bangkok"
  # Add more config here — NO rebuild needed when changed!
```

---

## 🧩 4. `secrets.yaml` — Sensitive Config (NOT committed!)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
# ⚠️ Use sealed-secrets or external-secrets in production
# Values below are PLACEHOLDERS — store in Vault/Secrets Manager
stringData:
  DATABASE_URL: "postgresql://user:password@db:5432/app"
  # NPM_TOKEN: "npm_xxxxxxx"
  # GIT_AUTH_TOKEN: "ghp_xxxxxxx"
  # API_SIGNING_KEY: "-----BEGIN PRIVATE KEY-----\n..."
```

---

## 🧩 5. Optional — Ingress (Public HTTP/HTTPS)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts: [ "app.yourdomain.com" ]
      secretName: app-tls
  rules:
    - host: app.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app
                port: { number: 80 }
```

---

## ✅ Key Design Features

### 🔒 Security
- **Non-root enforcement**: `runAsNonRoot: true` matches Dockerfile
- **Secrets separated from config**: DB URL/tokens → Secret; URLs → ConfigMap
- **No secrets in image**: All injected at runtime
- **Readiness before traffic**: `/health` must return 200 → pod marked ready

### 🔄 Deployment Safety
- **RollingUpdate strategy**: Old pods stay up until new ones are healthy
- **3 Probes**:
  - `startupProbe`: Give app time to start (max 60s)
  - `liveness`: Restart if app crashes/hangs
  - `readiness`: Don't send traffic until `/health` OK
- **Resource limits**: Prevent one app from starving others

### 🧩 Environment Promotion
```
Same image → dev → staging → prod
ConfigMap + Secrets change ONLY — NO rebuild!
```

### 📊 Health Endpoint Contract
```
GET /health → 200 OK
{ "status": "healthy", "version": "v1.2.3", "commit": "abc123" }
```
- Kubernetes uses this → only routes traffic when healthy
- Version/commit visible → confirm exactly what's running

---

## 🚀 Quick Start
```bash
# 1. Create namespace
kubectl create namespace app

# 2. Create config
kubectl apply -f configmap.yaml

# 3. Create secrets (use ExternalSecrets/Vault in prod!)
kubectl apply -f secrets.yaml

# 4. Deploy app
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# 5. Verify
kubectl rollout status deployment/app
kubectl get pods -w
kubectl get svc app
```

---

## ⚠️ Production Upgrade Checklist
- [ ] Replace plain `Secret` with **External Secrets Operator** or **Sealed Secrets**
- [ ] Add **Ingress + Cert-Manager** for HTTPS
- [ ] Set **image.tag** via CI → `:v1.2.3` not `:latest`
- [ ] Add **PodDisruptionBudget** → `minAvailable: 2`
- [ ] Add **Namespace NetworkPolicy**
- [ ] Configure **imagePullSecrets** for GHCR/Docker Hub

---

Want me to add **Horizontal Pod Autoscaler (HPA)**, **PodDisruptionBudget**, **ServiceMonitor/Prometheus**, or **Kustomize overlay templates** for dev/staging/prod promotion?
