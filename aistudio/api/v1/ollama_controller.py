import subprocess
from fastapi import APIRouter, HTTPException, Query
from aistudio.services.ollama_service import OllamaService
from aistudio.models.ollama_models import ModelListResponse, MessageResponse

router = APIRouter(prefix="/ollama", tags=["ollama"])


@router.get("/models", response_model=ModelListResponse)
def get_models():
    try:
        models = OllamaService.list_models()
        return ModelListResponse(models=models)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/load", response_model=MessageResponse)
def load_model(model_name: str = Query(..., description="Model name to load, e.g. llama3 or deepseek-r1")):
    try:
        models = OllamaService.list_models()
        if any(model.startswith(model_name) for model in models):
            return MessageResponse(message=f"Model {model_name} already loaded.")

        subprocess.run(
            ["ollama", "pull", model_name],
            check=True
        )
        return MessageResponse(message=f"Model {model_name} successfully pulled.")
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to pull model {model_name}: {e.stderr}")


@router.delete("/models/{model_name}", response_model=MessageResponse)
def delete_model(model_name: str):
    try:
        # Обрезаем тег :latest, если есть
        model_name = model_name.split(":")[0]
        result = subprocess.run(
            ["ollama", "rm", model_name],
            capture_output=True,
            text=True,
            check=True
        )
        return MessageResponse(message=f"Model {model_name} deleted.")
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete model {model_name}: {e.stderr or e.stdout or 'Unknown error'}"
        )
