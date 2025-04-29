#!/bin/bash
set -e

APP_NAME="my-parser-app"
NAMESPACE="default"
DOCKERFILE_PATH="."
TAG="latest"
K8S_DIR="./k8s"
JOB_NAME="one-time-parser"

echo "==> Строим Docker образ..."
eval $(minikube docker-env)
docker build -t $APP_NAME:$TAG $DOCKERFILE_PATH

echo "==> Удаляем старые ресурсы..."
kubectl delete -f $K8S_DIR/deployment.yaml --ignore-not-found
kubectl delete -f $K8S_DIR/job.yaml --ignore-not-found
kubectl delete -f $K8S_DIR/cronjob.yaml --ignore-not-found
kubectl delete -f $K8S_DIR/persistent-volume.yaml --ignore-not-found
kubectl delete -f $K8S_DIR/persistent-volume.yaml.template --ignore-not-found

echo "==> Создаём локальную директорию под данные, если не существует..."
DATA_DIR="$(pwd)/data"
mkdir -p "$DATA_DIR"

echo "==> Генерируем persistent-volume.yaml на основе шаблона..."
PV_TEMPLATE="$K8S_DIR/persistent-volume.yaml.template"
PV_RENDERED="$K8S_DIR/persistent-volume.yaml"

sed "s|__HOST_PATH__|$DATA_DIR|g" "$PV_TEMPLATE" >"$PV_RENDERED"

echo "==> Применяем Persistent Volume и Claim..."
kubectl apply -f "$PV_RENDERED"

echo "==> Создаём Deployment..."
kubectl apply -f $K8S_DIR/deployment.yaml

echo "==> Создаём Job..."
kubectl apply -f $K8S_DIR/job.yaml

echo "==> Ожидание создания пода Job..."
while true; do
  pod_name=$(kubectl get pods --selector=job-name=$JOB_NAME -o jsonpath='{.items[*].metadata.name}' 2>/dev/null)
  if [ -n "$pod_name" ]; then
    echo "==> Найден под: $pod_name"
    break
  fi
  sleep 2
done

echo "==> Подключаемся к логам пода (stream)..."
kubectl logs -f "$pod_name" &
LOGS_PID=$!

echo "==> Ожидаем завершения Job..."
while true; do
  status_succeeded=$(kubectl get job $JOB_NAME -o jsonpath='{.status.succeeded}' 2>/dev/null || echo "")
  status_failed=$(kubectl get job $JOB_NAME -o jsonpath='{.status.failed}' 2>/dev/null || echo "")

  if [ "$status_succeeded" == "1" ]; then
    echo "✅ Job завершён успешно!"
    kill $LOGS_PID 2>/dev/null || true
    wait $LOGS_PID 2>/dev/null || true
    break
  elif [ "$status_failed" != "" ] && [ "$status_failed" != "0" ]; then
    echo "❌ Job завершился с ошибкой!"
    kill $LOGS_PID 2>/dev/null || true
    wait $LOGS_PID 2>/dev/null || true
    echo "🔻 Повторный вывод последних логов:"
    kubectl logs "$pod_name"
    exit 1
  else
    sleep 10
  fi
done

echo "==> Создаём CronJob..."
kubectl apply -f $K8S_DIR/cronjob.yaml

echo "==> Всё готово:"
kubectl get all
