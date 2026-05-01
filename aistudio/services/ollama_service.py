import subprocess
from typing import List


class OllamaService:
    @staticmethod
    def list_models() -> List[str]:
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            models = result.stdout.strip().splitlines()
            return models
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to list models: {e}")

    @staticmethod
    def delete_model(model_name: str) -> None:
        try:
            subprocess.run(
                ["ollama", "delete", model_name],
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to delete model {model_name}: {e}")

    @staticmethod
    def load_model(model_name: str) -> None:
        models = OllamaService.list_models()
        if model_name not in models:
            raise RuntimeError(f"Model {model_name} not found")
        return
