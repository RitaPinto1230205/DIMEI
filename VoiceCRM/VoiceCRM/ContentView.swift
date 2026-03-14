//
//  ContentView.swift
//  VoiceCRM

import SwiftUI
import Speech
import AVFoundation

struct ContentView: View {
    @State private var isRecording = false
    @State private var transcribedText = "Carrega em Iniciar para começar..."
    @State private var statusMessage = ""
    
    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "pt-PT")) //reconhecer tuga for now
    
    private let audioEngine = AVAudioEngine() // motor de captura de som (buffers de 1024 amostras)

    @State private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest? //biblioteca nativa que converte a conversa em texto
    
    @State private var recognitionTask: SFSpeechRecognitionTask?
    
    var body: some View {
        VStack(spacing: 30) {
            
            Text("Voice CRM")
                .font(.largeTitle)
                .bold()
            
            ScrollView {
                Text(transcribedText)
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(height: 300)
            .background(Color(.systemGray6))
            .cornerRadius(12)
            .padding(.horizontal)
            
            Text(statusMessage)
                .foregroundColor(.gray)
                .font(.caption)
            
            Button(action: {
                if isRecording {
                    stopRecording()
                } else {
                    startRecording()
                }
            }) {
                Text(isRecording ? "⏹ Parar" : "🎙 Iniciar")
                    .font(.title2)
                    .bold()
                    .foregroundColor(.white)
                    .frame(width: 200, height: 60)
                    .background(isRecording ? Color.red : Color.blue)
                    .cornerRadius(30)
            }
        }
        .padding()
        .onAppear {
            requestPermissions()
        }
    }
    
    func requestPermissions() {
        SFSpeechRecognizer.requestAuthorization { status in
            DispatchQueue.main.async {
                switch status {
                case .authorized:
                    statusMessage = "Pronto para gravar"
                case .denied:
                    statusMessage = "Permissão de fala negada"
                case .restricted:
                    statusMessage = "Reconhecimento de fala não disponível"
                case .notDetermined:
                    statusMessage = "A aguardar permissão..."
                @unknown default:
                    statusMessage = "Estado desconhecido"
                }
            }
        }
    }
    
    func startRecording() {
        recognitionTask?.cancel()
        recognitionTask = nil
        
        let audioSession = AVAudioSession.sharedInstance()
        do {
            try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            statusMessage = "Erro ao configurar áudio: \(error.localizedDescription)"
            return
        }
        
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else { return }
        recognitionRequest.shouldReportPartialResults = true // é o que faz aparecer o texto em tempo real sem esperar acabar 
        
        recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { result, error in
            if let result = result {
                DispatchQueue.main.async {
                    transcribedText = result.bestTranscription.formattedString
                }
            }
            if error != nil {
                stopRecording()
            }
        }
        
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            recognitionRequest.append(buffer)
        }
        
        audioEngine.prepare()
        do {
            try audioEngine.start()
            isRecording = true
            transcribedText = ""
            statusMessage = "A gravar..."
        } catch {
            statusMessage = "Erro ao iniciar: \(error.localizedDescription)"
        }
    }
    
    func stopRecording() {
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
        isRecording = false
        statusMessage = "Gravação terminada"
    }
}

#Preview {
    ContentView()
}
