import os
import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression


def main():
    iris = load_iris()
    X = iris["data"]
    y = iris["target"]

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X, y)

    os.makedirs("models", exist_ok=True)
    model_path = os.path.join("models", "model.pkl")
    joblib.dump(model, model_path)

    print(f"Модель обучена и сохранена в {model_path}")


if __name__ == "__main__":
    main()
