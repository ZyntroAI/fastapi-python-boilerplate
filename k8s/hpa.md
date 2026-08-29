Verifying HPA details
 I need to verify the HPA (Hypothalamic-Pituitary-Adrenal) information from the web to ensure accuracy and tailor the YAML based on known names and assumptions.
Based on the names and resource values you provided, save this as k8s/hpa.yaml:

yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
  labels:
    app: fastapi
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-deployment

  minReplicas: 2
  maxReplicas: 10

  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60

    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 75

  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      selectPolicy: Max
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
        - type: Pods
          value: 2
          periodSeconds: 60

    scaleDown:
      stabilizationWindowSeconds: 300
      selectPolicy: Min
      policies:
        - type: Percent
          value: 25
          periodSeconds: 60
        - type: Pods
          value: 1
          periodSeconds: 60


Ensure the fastapi-deployment container defines resource requests:

yaml
resources:
  requests:
    cpu: 250m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi


Utilization targets are calculated relative to resource requests. The cluster also needs a working resource metrics API, commonly provided by Metrics Server. 12

Apply and inspect it with:

bash
kubectl apply -f k8s/hpa.yaml
kubectl get hpa fastapi-hpa
kubectl describe hpa fastapi-hpa
kubectl top pods


Adjust fastapi-deployment if the existing Deployment uses a different name.
