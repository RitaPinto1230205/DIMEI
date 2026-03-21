# Diagrama 1 — Arquitetura Geral do Sistema

```mermaid
graph TD
    subgraph iPad["iPad (Frontend - Swift)"]
        MIC[Microfone\nAVAudioEngine]
        VAD[VAD\nDetecção de Silêncio\n1.5s threshold]
        ASR[ASR\nSFSpeechRecognizer\npt-PT]
        RAM[RAM\nArray de Segmentos\nspeaker, text, timestamp]
        UI[Interface SwiftUI\nSegmentos + Locutor]
    end

    subgraph Backend["Backend - Python/Flask"]
        DIAR[Diarização\nMoshi / Pyannote]
        LLM[LLM\nExtração de Insights\nClaude / GPT]
        CRM[Modelo de Dados CRM\nPreferências, Intenções\nContexto, Resumo]
    end

    MIC -->|Audio stream PCM| VAD
    VAD -->|Segmento detectado| ASR
    ASR -->|Texto transcrito| RAM
    RAM -->|Segmentos JSON| DIAR
    DIAR -->|Locutor A/B| RAM
    RAM -->|Texto + Locutor| LLM
    LLM -->|Dados estruturados| CRM
    CRM -->|Registo final| UI
```
