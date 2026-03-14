//
//  ContentView.swift
//  VoiceCRM

import SwiftUI
import Speech
import AVFoundation

struct SpeechSegment: Identifiable {
    let id = UUID()
    let index: Int
    let text: String
    let timestamp: Date
    var speaker: String = "A identificar ..."
    
    var timeString: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter.string(from: timestamp)
    }
}

struct ContentView: View {
    @State private var isRecording = false
    @State private var currentText = ""
    @State private var segments: [SpeechSegment] = []
    @State private var statusMessage = "Pronto para gravar"
    @State private var segmentCount = 0
    
    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "pt-PT"))
    private let audioEngine = AVAudioEngine()
    @State private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    @State private var recognitionTask: SFSpeechRecognitionTask?
    
    @State private var silenceTimer: Timer?
    @State private var lastTextChange = Date()
    private let silenceThreshold: TimeInterval = 2.0
    
    var body: some View {
        NavigationView {
            VStack(spacing: 16) {
                
                if isRecording {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("A transcrever...")
                            .font(.caption)
                            .foregroundColor(.gray)
                        Text(currentText.isEmpty ? "..." : currentText)
                            .padding()
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Color.blue.opacity(0.1))
                            .cornerRadius(10)
                    }
                    .padding(.horizontal)
                }
                
                if segments.isEmpty {
                    Spacer()
                    Text("Os segmentos de fala vão aparecer aqui")
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.center)
                    Spacer()
                } else {
                    ScrollViewReader { proxy in
                        ScrollView {
                            LazyVStack(spacing: 10) {
                                ForEach(segments) { segment in
                                    SegmentView(segment: segment)
                                        .id(segment.id)
                                }
                            }
                            .padding(.horizontal)
                        }
                        .onChange(of: segments.count) {
                            if let last = segments.last {
                                proxy.scrollTo(last.id, anchor: .bottom)
                            }
                        }
                    }
                }
                
                Text(statusMessage)
                    .font(.caption)
                    .foregroundColor(.gray)
                
                HStack(spacing: 20) {
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
                            .frame(width: 160, height: 55)
                            .background(isRecording ? Color.red : Color.blue)
                            .cornerRadius(28)
                    }
                    
                    if !segments.isEmpty {
                        Button(action: {
                            segments = []
                            segmentCount = 0
                        }) {
                            Text("🗑 Limpar")
                                .font(.title2)
                                .foregroundColor(.white)
                                .frame(width: 120, height: 55)
                                .background(Color.gray)
                                .cornerRadius(28)
                        }
                    }
                }
                .padding(.bottom, 20)
            }
            .navigationTitle("Voice CRM")
            .navigationBarTitleDisplayMode(.large)
        }
        .onAppear {
            requestPermissions()
        }
    }
    
    func requestPermissions() {
        SFSpeechRecognizer.requestAuthorization { status in
            DispatchQueue.main.async {
                statusMessage = status == .authorized ? "Pronto para gravar" : "Permissão negada"
            }
        }
    }
    
    func startSilenceTimer() {
        silenceTimer?.invalidate()
        silenceTimer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { _ in
            let timeSinceLastChange = Date().timeIntervalSince(lastTextChange)
            if timeSinceLastChange >= silenceThreshold && !currentText.isEmpty {
                saveCurrentSegment()
            }
        }
    }
    
    func saveCurrentSegment() {
        guard !currentText.isEmpty else { return }
        segmentCount += 1
        let newSegment = SpeechSegment(
            index: segmentCount,
            text: currentText,
            timestamp: Date()
        )
        DispatchQueue.main.async {
            self.segments.append(newSegment)
            self.currentText = ""
            self.statusMessage = "Segmento \(self.segmentCount) guardado"
        }
        restartRecognition()
    }
    
    func startRecording() {
        recognitionTask?.cancel()
        recognitionTask = nil
        
        let audioSession = AVAudioSession.sharedInstance()
        do {
            try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            statusMessage = "Erro áudio: \(error.localizedDescription)"
            return
        }
        
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else { return }
        recognitionRequest.shouldReportPartialResults = true
        
        recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { result, error in
            if let result = result {
                DispatchQueue.main.async {
                    self.currentText = result.bestTranscription.formattedString
                    self.lastTextChange = Date()
                    self.statusMessage = "A gravar..."
                }
            }
            if let error = error {
                print("Erro: \(error)")
                self.saveCurrentSegment()
                if self.isRecording {
                    self.restartRecognition()
                }
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
            currentText = ""
            statusMessage = "A gravar..."
            startSilenceTimer()
        } catch {
            statusMessage = "Erro ao iniciar: \(error.localizedDescription)"
        }
    }
    
    func restartRecognition() {
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            if self.isRecording {
                self.startRecording()
            }
        }
    }
    
    func sendSegmentsToServer() {
        guard !segments.isEmpty else { return }
        
        let serverURL = URL(string: "http://192.168.1.178:5001/analyse")!
        var request = URLRequest(url: serverURL)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Prepara os segmentos para enviar
        let segmentsData = segments.map { seg in
            ["index": seg.index, "text": seg.text, "timestamp": seg.timeString] as [String: Any]
        }
        let body: [String: Any] = ["segments": segmentsData]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    self.statusMessage = "❌ \(error.localizedDescription)"
                    print("ERRO SERVIDOR: \(error)")
                }
                return
            }
            if let response = response as? HTTPURLResponse {
                print("STATUS HTTP: \(response.statusCode)")
            }
            if let data = data {
                print("RESPOSTA: \(String(data: data, encoding: .utf8) ?? "vazio")")
            }
            if let data = data,
               let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let resultSegments = json["segments"] as? [[String: Any]] {
                DispatchQueue.main.async {
                    // Atualiza os segmentos com o locutor do servidor
                    for result in resultSegments {
                        if let index = result["index"] as? Int,
                           let speaker = result["speaker"] as? String,
                           let idx = self.segments.firstIndex(where: { $0.index == index }) {
                            self.segments[idx] = SpeechSegment(
                                index: self.segments[idx].index,
                                text: self.segments[idx].text,
                                timestamp: self.segments[idx].timestamp,
                                speaker: speaker
                            )
                        }
                    }
                    self.statusMessage = "Análise concluída ✅"
                }
            }
        }.resume()
    }
    
    func stopRecording() {
        silenceTimer?.invalidate()
        silenceTimer = nil
        saveCurrentSegment()
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
        isRecording = false
        statusMessage = "Gravação terminada — \(segmentCount) segmentos"
        sendSegmentsToServer()
    }
}

struct SegmentView: View {
    let segment: SpeechSegment
    
    var speakerColor: Color {
        segment.speaker == "Locutor A" ? .blue : .green
    }
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text("\(segment.index)")
                .font(.caption)
                .bold()
                .foregroundColor(.white)
                .frame(width: 28, height: 28)
                .background(Color.blue)
                .clipShape(Circle())
            
            VStack(alignment: .leading, spacing: 4) {
                Text(segment.speaker)
                    .font(.caption)
                    .bold()
                    .foregroundStyle(speakerColor)
                Text(segment.text)
                    .font(.body)
                    .frame(maxWidth: .infinity, alignment: .leading)
                Text(segment.timeString)
                    .font(.caption2)
                    .foregroundColor(.gray)
            }
        }
        .padding(12)
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

#Preview {
    ContentView()
}
