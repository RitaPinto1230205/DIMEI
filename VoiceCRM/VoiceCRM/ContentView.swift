//
//  ContentView.swift
//  VoiceCRM

import SwiftUI
import Speech
import AVFoundation
import FluidAudio

struct SpeechSegment: Identifiable {
    let id = UUID()
    let index: Int
    let text: String
    let timestamp: Date
    var speaker: String = "A identificar..."
    var audioOffset: Int = 0

    var timeString: String {
        let f = DateFormatter()
        f.dateFormat = "HH:mm:ss"
        return f.string(from: timestamp)
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
    private let silenceThreshold: TimeInterval = 1.0

    @State private var recordingSampleRate: Double = 16000
    @State private var allAudioSamples: [Float] = []

    var body: some View {
        NavigationView {
            VStack(spacing: 16) {
                if isRecording {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("A transcrever...").font(.caption).foregroundColor(.gray)
                        Text(currentText.isEmpty ? "..." : currentText)
                            .padding()
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Color.blue.opacity(0.1))
                            .cornerRadius(10)
                    }.padding(.horizontal)
                }

                if segments.isEmpty {
                    Spacer()
                    Text("Os segmentos de fala vão aparecer aqui")
                        .foregroundColor(.gray).multilineTextAlignment(.center)
                    Spacer()
                } else {
                    ScrollViewReader { proxy in
                        ScrollView {
                            LazyVStack(spacing: 10) {
                                ForEach(segments) { seg in
                                    SegmentView(segment: seg).id(seg.id)
                                }
                            }.padding(.horizontal)
                        }
                        .onChange(of: segments.count) {
                            if let last = segments.last { proxy.scrollTo(last.id, anchor: .bottom) }
                        }
                    }
                }

                Text(statusMessage).font(.caption).foregroundColor(.gray)

                HStack(spacing: 20) {
                    Button(action: {
                        if isRecording {
                            stopRecording()
                        } else {
                            allAudioSamples = []
                            startRecording()
                        }
                    }) {
                        Text(isRecording ? "⏹ Parar" : "🎙 Iniciar")
                            .font(.title2).bold().foregroundColor(.white)
                            .frame(width: 160, height: 55)
                            .background(isRecording ? Color.red : Color.blue)
                            .cornerRadius(28)
                    }
                    if !segments.isEmpty {
                        Button(action: {
                            segments = []
                            segmentCount = 0
                            allAudioSamples = []
                        }) {
                            Text("🗑 Limpar")
                                .font(.title2).foregroundColor(.white)
                                .frame(width: 120, height: 55)
                                .background(Color.gray).cornerRadius(28)
                        }
                    }
                }.padding(.bottom, 20)
            }
            .navigationTitle("Voice CRM")
            .navigationBarTitleDisplayMode(.large)
        }
        .onAppear { requestPermissions() }
    }

    func requestPermissions() {
        SFSpeechRecognizer.requestAuthorization { status in
            DispatchQueue.main.async {
                statusMessage = status == .authorized ? "Pronto para gravar" : "Permissão negada"
            }
        }
    }

    func startRecording() {
        recognitionTask?.cancel()
        recognitionTask = nil

        let session = AVAudioSession.sharedInstance()
        try? session.setCategory(.record, mode: .measurement, options: .duckOthers)
        try? session.setActive(true, options: .notifyOthersOnDeactivation)

        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest else { return }
        recognitionRequest.shouldReportPartialResults = true

        recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { result, error in
            if let result = result {
                DispatchQueue.main.async {
                    self.currentText = result.bestTranscription.formattedString
                    self.lastTextChange = Date()
                    self.statusMessage = "A gravar..."
                }
            }
            if error != nil, self.isRecording { self.restartRecognition() }
        }

        let inputNode = audioEngine.inputNode
        let fmt = inputNode.outputFormat(forBus: 0)
        recordingSampleRate = fmt.sampleRate

        inputNode.installTap(onBus: 0, bufferSize: 4096, format: fmt) { buffer, _ in
            recognitionRequest.append(buffer)
            if let data = buffer.floatChannelData {
                let frames = Int(buffer.frameLength)
                let samples = Array(UnsafeBufferPointer(start: data[0], count: frames))
                DispatchQueue.main.async {
                    self.allAudioSamples.append(contentsOf: samples)
                }
            }
        }

        try? audioEngine.start()
        isRecording = true
        currentText = ""
        statusMessage = "A gravar..."
        startSilenceTimer()
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
        statusMessage = "A diarizar..."

        let allSamples = allAudioSamples
        let sr = recordingSampleRate

        Task {
            await runDiarization(samples: allSamples, sampleRate: sr)
        }
    }

    func runDiarization(samples: [Float], sampleRate: Double) async {
        let resampled = resampleTo16k(samples: samples, fromRate: sampleRate)
        guard resampled.count > 32000 else {
            DispatchQueue.main.async {
                self.statusMessage = "Gravação terminada — \(self.segmentCount) segmentos"
            }
            return
        }

        do {
            DispatchQueue.main.async { self.statusMessage = "A diarizar..." }

            let config = DiarizerConfig(
                clusteringThreshold: 0.7,
                minSpeechDuration: 2.0,
                minSilenceGap: 0.3
            )
            let models = try await DiarizerModels.downloadIfNeeded()
            let diarizer = DiarizerManager(config: config)
            diarizer.initialize(models: models)

            let result = try diarizer.performCompleteDiarization(resampled)

            print("Diarizer encontrou \(result.segments.count) segmentos")
            for s in result.segments {
                print("  Speaker \(s.speakerId): \(s.startTimeSeconds)s - \(s.endTimeSeconds)s")
            }

            DispatchQueue.main.async {
                self.assignSpeakers(diarizationResult: result)
            }
        } catch {
            print("Erro diarização: \(error)")
            DispatchQueue.main.async {
                self.statusMessage = "Gravação terminada — \(self.segmentCount) segmentos"
            }
        }
    }

    func assignSpeakers(diarizationResult: DiarizationResult) {
        guard !segments.isEmpty else { return }

        guard !diarizationResult.segments.isEmpty else {
            for i in 0..<segments.count {
                let seg = segments[i]
                segments[i] = SpeechSegment(index: seg.index, text: seg.text,
                                             timestamp: seg.timestamp, speaker: "Locutor A")
            }
            statusMessage = "Diarização concluída ✅ — \(segmentCount) segmentos"
            return
        }

        var speakerMap: [String: String] = [:]
        var nextLetter = 0

        for i in 0..<segments.count {
            let seg = segments[i]
            // Usa posição no áudio em vez de timestamp do relógio
            let segTime = Float(seg.audioOffset) / Float(recordingSampleRate)

            print("Segmento \(i): audioTime=\(segTime)s texto=\(seg.text)")

            var rawId = "\(diarizationResult.segments[0].speakerId)"
            var bestDist: Float = .greatestFiniteMagnitude

            for s in diarizationResult.segments {
                let center = (s.startTimeSeconds + s.endTimeSeconds) / 2
                let dist = abs(segTime - center)
                if dist < bestDist {
                    bestDist = dist
                    rawId = "\(s.speakerId)"
                }
            }

            if speakerMap[rawId] == nil {
                speakerMap[rawId] = "Locutor \(String(UnicodeScalar(65 + nextLetter)!))"
                nextLetter += 1
            }

            segments[i] = SpeechSegment(index: seg.index, text: seg.text,
                                         timestamp: seg.timestamp,
                                        speaker: speakerMap[rawId]!, audioOffset: seg.audioOffset)
        }
        statusMessage = "Diarização concluída ✅ — \(segmentCount) segmentos"
    }

    func restartRecognition() {
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            if self.isRecording { self.startRecording() }
        }
    }

    func startSilenceTimer() {
        silenceTimer?.invalidate()
        silenceTimer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { _ in
            if Date().timeIntervalSince(lastTextChange) >= silenceThreshold && !currentText.isEmpty {
                saveCurrentSegment()
            }
        }
    }

    func saveCurrentSegment() {
        guard !currentText.isEmpty else { return }
        segmentCount += 1
        var seg = SpeechSegment(index: segmentCount, text: currentText, timestamp: Date())
        seg.audioOffset = allAudioSamples.count
        segments.append(seg)
        currentText = ""
        statusMessage = "Segmento \(segmentCount) guardado"
        restartRecognition()
    }

    func resampleTo16k(samples: [Float], fromRate: Double) -> [Float] {
        guard fromRate != 16000 else { return samples }
        let ratio = 16000.0 / fromRate
        let outCount = Int(Double(samples.count) * ratio)
        guard outCount > 0 else { return [] }
        var output = [Float](repeating: 0, count: outCount)
        for i in 0..<outCount {
            let srcIdx = Double(i) / ratio
            let lo = Int(srcIdx)
            let hi = min(lo + 1, samples.count - 1)
            let frac = Float(srcIdx - Double(lo))
            output[i] = samples[lo] * (1 - frac) + samples[hi] * frac
        }
        return output
    }
}

struct SegmentView: View {
    let segment: SpeechSegment
    var speakerColor: Color {
        if segment.speaker.contains("A") { return .blue }
        if segment.speaker.contains("B") { return .green }
        if segment.speaker.contains("C") { return .orange }
        return .purple
    }

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text("\(segment.index)")
                .font(.caption).bold().foregroundColor(.white)
                .frame(width: 28, height: 28)
                .background(speakerColor).clipShape(Circle())
            VStack(alignment: .leading, spacing: 4) {
                Text(segment.speaker).font(.caption).bold().foregroundStyle(speakerColor)
                Text(segment.text).font(.body).frame(maxWidth: .infinity, alignment: .leading)
                Text(segment.timeString).font(.caption2).foregroundColor(.gray)
            }
        }
        .padding(12)
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

#Preview { ContentView() }
