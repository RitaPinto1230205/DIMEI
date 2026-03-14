# DIMEI — Sistema de Extração de Informação Verbal para CRM no Retalho de Luxo

Sistema de extração de informação verbal para CRM no retalho de luxo.

## Stack Tecnológica
- **Frontend:** Swift / SwiftUI (iOS)
- **Reconhecimento de fala:** SFSpeechRecognizer (nativo iOS)
- **Captura de áudio:** AVAudioEngine (nativo iOS)
- **Backend (futuro):** Python / Node.js

## Iteração 1 — Pipeline Básico ASR ✅
**Objetivo:** capturar áudio em tempo real e transcrever para texto.

### O que foi feito:
- Criação do projeto iOS em SwiftUI
- Configuração de permissões de microfone e reconhecimento de fala
- Implementação de captura de áudio contínua com AVAudioEngine
- Transcrição em tempo real com SFSpeechRecognizer (pt-PT)
- Interface simples com botão iniciar/parar e área de texto

### Limitações conhecidas (a resolver nas próximas iterações):
- SFSpeechRecognizer para automaticamente após silêncio prolongado
- Não distingue diferentes locutores (sem diarização)
- Degrada com sobreposição de vozes

## Próximos passos — Iteração 2
- Investigar bibliotecas de diarização (Moshi, pyannote)
- Separar voz do consultor vs. cliente
- Implementar VAD (Voice Activity Detection) para gerir silêncios
