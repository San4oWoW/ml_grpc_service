import os
import logging
from concurrent import futures

import grpc
import joblib
import numpy as np

from protos import model_pb2, model_pb2_grpc


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_model(model_path: str):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    model = joblib.load(model_path)
    logger.info("Model loaded from %s", model_path)
    return model


class PredictionServiceServicer(model_pb2_grpc.PredictionServiceServicer):
    def __init__(self, model, model_version: str):
        self.model = model
        self.model_version = model_version

    def Health(self, request, context):
        response = model_pb2.HealthResponse(
            status="ok",
            modelVersion=self.model_version
        )
        return response

    def Predict(self, request, context):
        try:
            features = list(request.features)
            if not features:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("features must not be empty")
                return model_pb2.PredictResponse()

            x = np.array(features, dtype=float).reshape(1, -1)

            y_pred = self.model.predict(x)[0]

            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba(x)[0]
                confidence = float(np.max(proba))
            else:
                confidence = 0.5

            response = model_pb2.PredictResponse(
                prediction=str(y_pred),
                confidence=confidence,
                modelVersion=self.model_version
            )
            return response

        except Exception as e:
            logger.exception("Error during prediction")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Prediction error: {e}")
            return model_pb2.PredictResponse()


def serve():
    port = int(os.getenv("PORT", "50051"))
    model_path = os.getenv("MODEL_PATH", "/models/model.pkl")
    model_version = os.getenv("MODEL_VERSION", "v1.0.0")

    logger.info("Starting gRPC server on port %d", port)
    logger.info("Using model at %s", model_path)
    logger.info("Model version: %s", model_version)

    model = load_model(model_path)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    servicer = PredictionServiceServicer(
        model=model,
        model_version=model_version
    )

    model_pb2_grpc.add_PredictionServiceServicer_to_server(servicer, server)

    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info("Server started. Listening on port %d", port)

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
