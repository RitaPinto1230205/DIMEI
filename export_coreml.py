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
from speechbrain.pretrained import EncoderClassifier

print("Loading ECAPA-TDNN...")
classifier = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa-voxceleb",
    run_opts={"device": "cpu"},
)
classifier.eval()


class SpeakerEncoderWrapper(nn.Module):
    """Wraps the full pipeline: raw audio (16kHz mono) -> normalized embedding."""
    def __init__(self, classifier):
        super().__init__()
        self.compute_features = classifier.mods["compute_features"]
        self.mean_var_norm = classifier.mods["mean_var_norm"]
        self.embedding_model = classifier.mods["embedding_model"]
        self.mean_var_norm_emb = classifier.mods["mean_var_norm_emb"]

    def forward(self, wav):
        # wav: (1, time) — mono 16kHz
        feats = self.compute_features(wav)                          # (1, frames, 80)
        lens = torch.ones(feats.shape[0])
        feats = self.mean_var_norm(feats, lens)                     # normalise
        embedding = self.embedding_model(feats)                     # (1, 1, 192)
        embedding = self.mean_var_norm_emb(embedding, lens)         # normalise
        embedding = embedding.squeeze()                             # (192,)
        # L2 normalise
        return embedding / embedding.norm()


model = SpeakerEncoderWrapper(classifier).eval()

# Trace with 2s of audio at 16kHz
dummy_input = torch.randn(1, 32000)
with torch.no_grad():
    traced = torch.jit.trace(model, dummy_input)

print("Converting to CoreML...")
mlmodel = ct.convert(
    traced,
    inputs=[ct.TensorType(name="audio", shape=(1, ct.RangeDim(8000, 160000)))],
    outputs=[ct.TensorType(name="embedding")],
    minimum_deployment_target=ct.target.iOS16,
)

mlmodel.short_description = "ECAPA-TDNN speaker embedding — VoiceCRM"
mlmodel.save("SpeakerEncoder.mlpackage")
print("✅ Saved: SpeakerEncoder.mlpackage — drag into Xcode!")
