name: CI/CD Deploy Payments Platform (Staging)

on:
  push:
    branches:
      - develop
  workflow_dispatch:

jobs:
  build-and-deploy-staging:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Setup Helm & Kubectl
        uses: azure/setup-helm@v4
        with: { version: v3.14.0 }
      - name: Setup Kubectl
        uses: azure/setup-kubectl@v4
        with: { version: v1.30.0 }

      - name: Configure Kubeconfig (Staging)
        run: |
          echo "${{ secrets.KUBECONFIG_STAGING }}" > kubeconfig.yaml
          export KUBECONFIG=$PWD/kubeconfig.yaml

      - name: Login to Container Registry
        run: |
          echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login ${{ secrets.REGISTRY }} -u ${{ secrets.REGISTRY_USER }} --password-stdin

      - name: Build & Push API (Staging Tag)
        run: |
          docker build -t ${{ secrets.REGISTRY }}/api:staging-${{ github.sha }} ./api
          docker push ${{ secrets.REGISTRY }}/api:staging-${{ github.sha }}

      - name: Build & Push Skip-Payment (Staging Tag)
        run: |
          docker build -t ${{ secrets.REGISTRY }}/skip-payment:staging-${{ github.sha }} ./skip-payment
          docker push ${{ secrets.REGISTRY }}/skip-payment:staging-${{ github.sha }}

      - name: Helm dependency update
        run: helm dependency update ./payments-helm-chart

      - name: Helm Upgrade/Install (Staging)
        run: |
          helm upgrade --install payments-platform-staging ./payments-helm-chart \
            -n payments-staging --create-namespace \
            -f ./payments-helm-chart/values-staging.yaml \
            --set api.image.tag=staging-${{ github.sha }} \
            --set skip-payment.image.tag=staging-${{ github.sha }}
