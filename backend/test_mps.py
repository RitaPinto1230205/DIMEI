import torch

if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("✅ GPU M1 (MPS) disponível!")
else:
    device = torch.device("cpu")
    print("⚠️ Usando CPU")

print(f"Device: {device}")
