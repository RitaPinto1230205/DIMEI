"""
Exports ECAPA-TDNN (speechbrain) to CoreML format for on-device speaker diarization.

Run once with:
    pip3 install "speechbrain==0.5.16" "torch==2.2.2" "torchaudio==2.2.2" "numpy<2" "coremltools==7.2" "huggingface_hub==0.23.4" requests
    python3 export_coreml.py

Output: SpeakerEncoder.mlpackage  (drag into Xcode)
"""
import torch
import torch.nn as nn
import coremltools as ct
import numpy as np
from speechbrain.pretrained import EncoderClassifier

print("Loading ECAPA-TDNN...")
classifier = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa-voxceleb",
    run_opts={"device": "cpu"},
)
classifier.eval()


class SpeakerEncoderWrapper(nn.Module):
    """Wraps only the embedding model — feats (mel filterbank) -> embedding.
    compute_features and mean_var_norm excluded — data-dependent control flow
    breaks torch.jit.trace. Mel features computed separately in Swift.
    """
    def __init__(self, classifier):
        super().__init__()
        self.embedding_model = classifier.mods["embedding_model"]

    def forward(self, feats):
        # feats: (1, frames, 80) — mel filterbank features at 16kHz
        embedding = self.embedding_model(feats)
        embedding = embedding.squeeze()
        norm = embedding.norm()
        result = embedding / (norm + 1e-8)
        return result.float()


model = SpeakerEncoderWrapper(classifier).eval()

dummy_input = torch.randn(1, 100, 80)
with torch.no_grad():
    traced = torch.jit.trace(model, dummy_input)
    test_out = traced(dummy_input)
    print(f"Traced model test — shape: {test_out.shape} | primeiros 5: {test_out[:5].tolist()}")

print("Converting to CoreML...")
mlmodel = ct.convert(
    traced,
    inputs=[ct.TensorType(name="feats", shape=(1, ct.RangeDim(50, 2000), 80))],
    outputs=[ct.TensorType(name="embedding")],
    compute_precision=ct.precision.FLOAT32,
    minimum_deployment_target=ct.target.iOS15,
)

mlmodel.short_description = "ECAPA-TDNN speaker embedding — VoiceCRM"
mlmodel.save("SpeakerEncoder.mlpackage")
print("✅ Saved: SpeakerEncoder.mlpackage — drag into Xcode!")

loaded = ct.models.MLModel("SpeakerEncoder.mlpackage")
test_feats = np.random.randn(1, 100, 80).astype(np.float32)
result = loaded.predict({"feats": test_feats})
print(f"Verificação Python — primeiros 5: {result['embedding'][:5]}")
