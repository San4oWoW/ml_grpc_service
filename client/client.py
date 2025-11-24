import os
import grpc

from protos import model_pb2, model_pb2_grpc


def make_health_request(stub):
    response = stub.Health(model_pb2.HealthRequest())
    print("Health response:")
    print(f"  status: {response.status}")
    print(f"  modelVersion: {response.modelVersion}")


def make_predict_request(stub):
    # Для Iris модель ожидает 4 признака (sepal length, sepal width, petal length, petal width)
    features = [5.1, 3.5, 1.4, 0.2]

    request = model_pb2.PredictRequest(features=features)
    response = stub.Predict(request)

    print("Predict response:")
    print(f"  prediction: {response.prediction}")
    print(f"  confidence: {response.confidence:.4f}")
    print(f"  modelVersion: {response.modelVersion}")


def main():
    host = os.getenv("GRPC_HOST", "localhost")
    port = os.getenv("GRPC_PORT", "50051")
    target = f"{host}:{port}"

    with grpc.insecure_channel(target) as channel:
        stub = model_pb2_grpc.PredictionServiceStub(channel)

        print(f"Connected to gRPC server at {target}")

        make_health_request(stub)
        print("-" * 40)
        make_predict_request(stub)


if __name__ == "__main__":
    main()
