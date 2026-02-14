# deploy.ps1 - ADK Frontend Deployment Script
$PROJECT_ID = "adk-sandbox-486117" # Proyecto: adk-sandbox
$REGION = "us-central1"
$SERVICE_NAME = "adk-people-analytics-frontend"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host "🚀 Iniciando despliegue de Producción via Cloud Build..." -ForegroundColor Cyan

# 1. Construir la imagen en la NUBE (Evita depender de Docker local)
Write-Host "📦 Construyendo imagen en Google Cloud Build..." -ForegroundColor Yellow
gcloud builds submit --tag $IMAGE_NAME .

# 2. Desplegar en Cloud Run
Write-Host "🌐 Desplegando en Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --set-env-vars "APP_MODE=production,PYTHON_ENV=production,BACKEND_URL=https://adk-people-analytics-backend-828393973311.us-central1.run.app" `
    --memory 1Gi `
    --cpu 1

Write-Host "✅ Despliegue completado con éxito!" -ForegroundColor Green
