import torch
from moshi.models import loaders

print("A carregar Moshi...")
moshi_weight = loaders.hf_hub_download(
    repo_id='kyutai/moshiko-pytorch-bf16',
    filename='model.safetensors'
)
print(f"Modelo encontrado: {moshi_weight}")
print("✅ Moshi instalado com sucesso!")
