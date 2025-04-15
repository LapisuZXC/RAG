set -e     # chmod -x deploy.sh           ./deploy.sh

APP_NAME="my-parser-app"
NAMESPACE="default"
DOCKERFILE_PATH="."
TAG="latest"
K8S_DIR="./k8s"

echo "==> Строим Docker образ..."
eval $(minikube docker-env)     # eval $(minikube docker-env -u) для возврата
docker build -t $APP_NAME:$TAG $DOCKERFILE_PATH

echo "==> Удаляем старые ресурсы..."
kubectl delete $K8S_DIR/deployment.yaml --ignore-not-found
kubectl delete $K8S_DIR/job.yaml  --ignore-not-found
kubectl delete $K8S_DIR/cronjob.yaml  --ignore-not-found
kubectl delete $K8S_DIR/persistent-volume.yaml  --ignore-not-found


echo "==> Создаём Persistent Volume и Claim..."
kubectl apply -f $K8S_DIR/persistent-volume.yaml

echo "==> Создаём Deployment..."
kubectl apply -f $K8S_DIR/deployment.yaml

echo "==> Создаём Job..."
kubectl apply -f $K8S_DIR/job.yaml

echo "==> Создаём Crom=nJob..."
kubectl apply -f $K8S_DIR/cronjob.yaml

echo "==> Всё, лафа кончилась, дальше сам :)"
kubectl get all