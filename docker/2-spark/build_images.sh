docker build \
  -f 1-cluster-base.Dockerfile \
  -t cluster-base .

docker build \
  -f 2-spark-base.Dockerfile \
  -t spark-base .

docker build \
  -f 3-spark-master.Dockerfile \
  -t spark-master .

docker build \
  -f 4-spark-worker.Dockerfile \
  -t spark-worker .
