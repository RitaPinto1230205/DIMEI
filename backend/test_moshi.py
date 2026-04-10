import os
from moshi.models import loaders


def test_moshi_model_downloads():
    path = loaders.hf_hub_download(
        repo_id='kyutai/moshiko-pytorch-bf16',
        filename='model.safetensors'
    )
    assert os.path.exists(path), f"Modelo não encontrado em: {path}"
    assert path.endswith('.safetensors')
