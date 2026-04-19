//
//  ContentView.swift
//  VoiceCRM
//  Diarização com FluidAudio + enrolamento do consultor

import SwiftUI
import Speech
import AVFoundation
import FluidAudio

struct ContentView: View {
    @State private var isRecording = false
    @State private var currentText = ""
    @State private var segments: [SpeechSegment] = []
    @State private var statusMessage = "Pronto para gravar"
    @State private var segmentCount = 0
    @State private var showEnrollmentSheet = false
    @State private var isEnrolled = false
    @State private var isRestartingRecognition = false

    @State private var consultantEnrollmentSamples16k: [Float] = []

    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "pt-PT"))
    private let audioEngine = AVAudioEngine()

    @State private var diarizer = DiarizerManager()

    @State private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    @State private var recognitionTask: SFSpeechRecognitionTask?
    @State private var silenceTimer: Timer?
    @State private var lastTextChange = Date()

    private let silenceThreshold: TimeInterval = 0.85

    @State private var recordingSampleRate: Double = 16000
    @State private var currentSegmentSamples: [Float] = []
    @State private var allAudioSamples: [Float] = []

    var body: some View {
        NavigationView {
            VStack(spacing: 16) {
                enrollmentHeader

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
                    Text("Os segmentos vão aparecer aqui")
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

                controls
            }
            .navigationTitle("Voice CRM")
            .navigationBarTitleDisplayMode(.large)
            .sheet(isPresented: $showEnrollmentSheet) {
                EnrollmentView(
                    isEnrolled: $isEnrolled,
                    consultantEnrollmentSamples16k: $consultantEnrollmentSamples16k
                )
            }
        }
        .onAppear {
            requestPermissions()
        }
    }

    private var enrollmentHeader: some View {
        Group {
            if !isEnrolled {
                Button {
                    showEnrollmentSheet = true
                } label: {
                    HStack {
                        Image(systemName: "person.crop.circle.badge.plus")
                        Text("Fazer enrolamento do consultor")
                            .bold()
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.orange)
                    .cornerRadius(12)
                }
                .padding(.horizontal)
            } else {
                HStack {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)

                    Text("Consultor identificado")
                        .foregroundColor(.green)
                        .font(.caption)
                        .bold()

                    Spacer()

                    Button("Refazer") {
                        isEnrolled = false
                        consultantEnrollmentSamples16k = []
                        showEnrollmentSheet = true
                    }
                    .font(.caption)
                    .foregroundColor(.orange)
                }
                .padding(.horizontal)
            }
        }
    }

    private var controls: some View {
        HStack(spacing: 20) {
            Button {
                if isRecording {
                    stopRecording()
                } else {
                    allAudioSamples = []
                    currentSegmentSamples = []
                    startRecording()
                }
            } label: {
                Text(isRecording ? "⏹ Parar" : "🎙 Iniciar")
                    .font(.title2)
                    .bold()
                    .foregroundColor(.white)
                    .frame(width: 160, height: 55)
                    .background(isRecording ? Color.red : Color.blue)
                    .cornerRadius(28)
            }

            if !segments.isEmpty {
                Button {
                    segments = []
                    segmentCount = 0
                    allAudioSamples = []
                    currentSegmentSamples = []
                } label: {
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

    func requestPermissions() {
        SFSpeechRecognizer.requestAuthorization { status in
            DispatchQueue.main.async {
                statusMessage = status == .authorized ? "Pronto para gravar" : "Permissão de fala negada"
            }
        }

        AVAudioSession.sharedInstance().requestRecordPermission { granted in
            DispatchQueue.main.async {
                if !granted {
                    statusMessage = "Permissão de microfone negada"
                }
            }
        }
    }

    func startRecording() {
        recognitionTask?.cancel()
        recognitionTask = nil

        let session = AVAudioSession.sharedInstance()

        do {
            try session.setCategory(.record, mode: .measurement, options: .duckOthers)
            try session.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            statusMessage = "Erro ao ativar áudio"
            return
        }

        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()

        guard let recognitionRequest else {
            statusMessage = "Erro ao iniciar reconhecimento"
            return
        }

        recognitionRequest.shouldReportPartialResults = true

        recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { result, error in
            if let result {
                DispatchQueue.main.async {
                    self.currentText = result.bestTranscription.formattedString
                    self.lastTextChange = Date()
                    self.statusMessage = "A gravar..."
                }
            }

            if let error, self.isRecording {
                let nsError = error as NSError

                if nsError.domain == "kLSRErrorDomain", nsError.code == 301 {
                    return
                }

                if nsError.domain == "kAFAssistantErrorDomain", nsError.code == 1110 {
                    DispatchQueue.main.async {
                        self.statusMessage = "À espera de fala..."
                    }
                    self.restartRecognition(after: 2.0)
                    return
                }

                self.restartRecognition(after: 0.5)
            }
        }

        let inputNode = audioEngine.inputNode
        let format = inputNode.outputFormat(forBus: 0)

        recordingSampleRate = format.sampleRate

        inputNode.removeTap(onBus: 0)

        inputNode.installTap(onBus: 0, bufferSize: 4096, format: format) { buffer, _ in
            recognitionRequest.append(buffer)

            guard let data = buffer.floatChannelData else { return }

            let frames = Int(buffer.frameLength)
            let samples = Array(UnsafeBufferPointer(start: data[0], count: frames))

            DispatchQueue.main.async {
                self.allAudioSamples.append(contentsOf: samples)
                self.currentSegmentSamples.append(contentsOf: samples)
            }
        }

        do {
            audioEngine.prepare()
            try audioEngine.start()
        } catch {
            statusMessage = "Erro ao iniciar microfone"
            return
        }

        isRecording = true
        currentText = ""
        lastTextChange = Date()
        statusMessage = "A gravar..."

        startSilenceTimer()
    }

    func stopRecording() {
        silenceTimer?.invalidate()
        silenceTimer = nil

        saveCurrentSegment(shouldRestartRecognition: false)

        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)

        recognitionRequest?.endAudio()
        recognitionTask?.cancel()

        recognitionRequest = nil
        recognitionTask = nil

        isRestartingRecognition = false
        isRecording = false
        currentText = ""

        guard isEnrolled, !consultantEnrollmentSamples16k.isEmpty else {
            statusMessage = "Gravação terminada — falta enrolamento do consultor"
            return
        }

        let conversationSamples16k = resampleTo16k(
            samples: allAudioSamples,
            fromRate: recordingSampleRate
        )

        statusMessage = "A processar diarização..."

        Task {
            await diarizeAndUpdateSegments(conversationSamples16k: conversationSamples16k)
        }
    }

    func restartRecognition(after delay: TimeInterval = 0.15) {
        guard isRecording else { return }
        guard !isRestartingRecognition else { return }

        isRestartingRecognition = true

        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)

        recognitionRequest?.endAudio()
        recognitionTask?.cancel()

        recognitionRequest = nil
        recognitionTask = nil

        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
            self.isRestartingRecognition = false

            if self.isRecording {
                self.startRecording()
            }
        }
    }

    func startSilenceTimer() {
        silenceTimer?.invalidate()

        silenceTimer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { _ in
            if Date().timeIntervalSince(lastTextChange) >= silenceThreshold,
               !currentText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                saveCurrentSegment()
            }
        }
    }

    func saveCurrentSegment(shouldRestartRecognition: Bool = true) {
        let text = currentText.trimmingCharacters(in: .whitespacesAndNewlines)

        guard !text.isEmpty else {
            return
        }

        let endTime = Double(allAudioSamples.count) / recordingSampleRate
        let duration = Double(currentSegmentSamples.count) / recordingSampleRate
        let startTime = max(0, endTime - duration)

        segmentCount += 1

        let segment = SpeechSegment(
            index: segmentCount,
            text: text,
            timestamp: Date(),
            startTime: startTime,
            endTime: endTime,
            speaker: "A identificar..."
        )

        segments.append(segment)

        currentSegmentSamples = []
        currentText = ""
        statusMessage = "Segmento \(segmentCount)"

        if shouldRestartRecognition, isRecording {
            restartRecognition()
        }
    }

    func diarizeAndUpdateSegments(conversationSamples16k: [Float]) async {
        do {
            let oneSecondSilence = [Float](repeating: 0, count: 16000)

            let combinedSamples = consultantEnrollmentSamples16k + oneSecondSilence + conversationSamples16k

            let enrollmentStart = 0.0
            let enrollmentEnd = Double(consultantEnrollmentSamples16k.count) / 16000.0
            let conversationOffset = Double(consultantEnrollmentSamples16k.count + oneSecondSilence.count) / 16000.0

            let models = try await DiarizerModels.downloadIfNeeded()
            diarizer.initialize(models: models)

            let result = try diarizer.performCompleteDiarization(combinedSamples)

            let consultantSpeakerId = dominantSpeakerId(
                in: result.segments,
                from: enrollmentStart,
                to: enrollmentEnd,
                speakerId: { String($0.speakerId) },
                startTime: { Double($0.startTimeSeconds) },
                endTime: { Double($0.endTimeSeconds) }
            )
            
            await MainActor.run {
                guard let consultantSpeakerId else {
                    statusMessage = "Não consegui identificar o consultor no enrolamento"
                    return
                }

                for index in segments.indices {
                    let segmentStart = segments[index].startTime + conversationOffset
                    let segmentEnd = segments[index].endTime + conversationOffset

                    let speakerId = dominantSpeakerId(
                        in: result.segments,
                        from: segmentStart,
                        to: segmentEnd,
                        speakerId: { String($0.speakerId) },
                        startTime: { Double($0.startTimeSeconds) },
                        endTime: { Double($0.endTimeSeconds) }
                    )
                    
                    if speakerId == consultantSpeakerId {
                        segments[index].speaker = "Consultor"
                    } else {
                        segments[index].speaker = "Cliente"
                    }
                }

                statusMessage = "Gravação terminada — \(segmentCount) segmentos"
            }
        } catch {
            await MainActor.run {
                statusMessage = "Erro na diarização: \(error.localizedDescription)"
            }
        }
    }

    func dominantSpeakerId<Segment>(
        in diarizationSegments: [Segment],
        from start: Double,
        to end: Double,
        speakerId: (Segment) -> String,
        startTime: (Segment) -> Double,
        endTime: (Segment) -> Double
    ) -> String? {
        var scores: [String: Double] = [:]

        for segment in diarizationSegments {
            let overlapStart = max(start, startTime(segment))
            let overlapEnd = min(end, endTime(segment))
            let overlap = overlapEnd - overlapStart

            if overlap > 0 {
                scores[speakerId(segment), default: 0] += overlap
            }
        }

        return scores.max(by: { $0.value < $1.value })?.key
    }
    
    func resampleTo16k(samples: [Float], fromRate: Double) -> [Float] {
        guard !samples.isEmpty else { return [] }

        if abs(fromRate - 16000) < 1 {
            return samples
        }

        let ratio = 16000.0 / fromRate
        let outputCount = Int(Double(samples.count) * ratio)

        guard outputCount > 0 else {
            return []
        }

        var output = [Float](repeating: 0, count: outputCount)

        for i in 0..<outputCount {
            let sourceIndex = Double(i) / ratio
            let low = Int(sourceIndex)
            let high = min(low + 1, samples.count - 1)
            let fraction = Float(sourceIndex - Double(low))

            output[i] = samples[low] * (1 - fraction) + samples[high] * fraction
        }

        return output
    }
}

// MARK: - Enrollment View

struct EnrollmentView: View {
    @Binding var isEnrolled: Bool
    @Binding var consultantEnrollmentSamples16k: [Float]

    @Environment(\.dismiss) private var dismiss

    private let audioEngine = AVAudioEngine()

    @State private var isRecording = false
    @State private var countdown = 10
    @State private var enrollmentSamples: [Float] = []
    @State private var statusText = "Fala durante 10 segundos para enrolar o consultor"
    @State private var timer: Timer?
    @State private var sampleRate: Double = 16000

    var body: some View {
        VStack(spacing: 30) {
            Text("Enrolamento do Consultor")
                .font(.title2)
                .bold()

            Text(statusText)
                .multilineTextAlignment(.center)
                .foregroundColor(.gray)
                .padding(.horizontal)

            if isRecording {
                Text("\(countdown)")
                    .font(.system(size: 80, weight: .bold))
                    .foregroundColor(.red)
            }

            Button {
                if !isRecording {
                    startEnrollment()
                }
            } label: {
                Text(isRecording ? "A gravar..." : "🎙 Iniciar Enrolamento")
                    .font(.title3)
                    .bold()
                    .foregroundColor(.white)
                    .frame(width: 250, height: 55)
                    .background(isRecording ? Color.red : Color.orange)
                    .cornerRadius(28)
            }
            .disabled(isRecording)

            Button("Cancelar") {
                stopAudioOnly()
                dismiss()
            }
            .foregroundColor(.gray)
        }
        .padding(40)
    }

    func startEnrollment() {
        enrollmentSamples = []
        countdown = 10
        isRecording = true
        statusText = "Fala normalmente durante 10 segundos..."

        let session = AVAudioSession.sharedInstance()

        do {
            try session.setCategory(.record, mode: .measurement, options: .duckOthers)
            try session.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            statusText = "Erro ao ativar áudio"
            return
        }

        let inputNode = audioEngine.inputNode
        let format = inputNode.outputFormat(forBus: 0)

        sampleRate = format.sampleRate

        inputNode.removeTap(onBus: 0)

        inputNode.installTap(onBus: 0, bufferSize: 4096, format: format) { buffer, _ in
            guard let data = buffer.floatChannelData else { return }

            let frames = Int(buffer.frameLength)
            let samples = Array(UnsafeBufferPointer(start: data[0], count: frames))

            DispatchQueue.main.async {
                self.enrollmentSamples.append(contentsOf: samples)
            }
        }

        do {
            audioEngine.prepare()
            try audioEngine.start()
        } catch {
            statusText = "Erro ao iniciar microfone"
            return
        }

        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            DispatchQueue.main.async {
                if self.countdown > 1 {
                    self.countdown -= 1
                } else {
                    self.stopEnrollment()
                }
            }
        }
    }

    func stopEnrollment() {
        timer?.invalidate()
        timer = nil

        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)

        isRecording = false

        let resampled = resampleTo16k(
            samples: enrollmentSamples,
            fromRate: sampleRate
        )

        guard resampled.count >= 16000 * 3 else {
            statusText = "Enrolamento demasiado curto — tenta novamente"
            return
        }

        consultantEnrollmentSamples16k = resampled
        isEnrolled = true
        statusText = "Enrolamento concluído"

        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            dismiss()
        }
    }

    func stopAudioOnly() {
        timer?.invalidate()
        timer = nil

        if audioEngine.isRunning {
            audioEngine.stop()
            audioEngine.inputNode.removeTap(onBus: 0)
        }

        isRecording = false
    }

    func resampleTo16k(samples: [Float], fromRate: Double) -> [Float] {
        guard !samples.isEmpty else { return [] }

        if abs(fromRate - 16000) < 1 {
            return samples
        }

        let ratio = 16000.0 / fromRate
        let outputCount = Int(Double(samples.count) * ratio)

        guard outputCount > 0 else {
            return []
        }

        var output = [Float](repeating: 0, count: outputCount)

        for i in 0..<outputCount {
            let sourceIndex = Double(i) / ratio
            let low = Int(sourceIndex)
            let high = min(low + 1, samples.count - 1)
            let fraction = Float(sourceIndex - Double(low))

            output[i] = samples[low] * (1 - fraction) + samples[high] * fraction
        }

        return output
    }
}

// MARK: - Data Model

struct SpeechSegment: Identifiable {
    let id = UUID()
    let index: Int
    let text: String
    let timestamp: Date
    let startTime: Double
    let endTime: Double
    var speaker: String

    var timeString: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter.string(from: timestamp)
    }
}

// MARK: - Segment View

struct SegmentView: View {
    let segment: SpeechSegment

    var speakerColor: Color {
        if segment.speaker == "Consultor" {
            return .blue
        }

        if segment.speaker == "Cliente" {
            return .green
        }

        return .orange
    }

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text("\(segment.index)")
                .font(.caption)
                .bold()
                .foregroundColor(.white)
                .frame(width: 28, height: 28)
                .background(speakerColor)
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
