//
//  ContentView.swift
//  VoiceCRM
//  Diarização com FluidAudio + enrolamento do consultor

import SwiftUI
import Speech
import AVFoundation
import FluidAudio

// MARK: - CRM Data Model

struct CRMProfile: Codable {
    struct ClientProfile: Codable {
        var gender: String?
        var age_range: String?
        var residence: String?
        var client_tier: String?
        var style_preferences: [String]?
        var fabric_preferences: [String]?
        var sizes: Sizes?

        struct Sizes: Codable {
            var clothing: String?
            var shoes: String?
            var other: String?
        }
    }

    struct PurchaseHistory: Codable {
        var products_owned: [String]?
        var estimated_spend: String?
        var purchase_frequency: String?
    }

    struct FamilyRelation: Codable {
        var relation: String?
        var name: String?
        var occasions: [String]?
        var preferences: [String]?
    }

    struct Memory: Codable {
        var category: String?
        var content: String?
        var date_mentioned: String?
    }

    struct CurrentVisit: Codable {
        var products_mentioned: [String]?
        var purchase_intent: String?
        var budget_range: String?
        var occasion: String?
    }

    var client_profile: ClientProfile?
    var purchase_history: PurchaseHistory?
    var family_relations: [FamilyRelation]?
    var memories: [Memory]?
    var current_visit: CurrentVisit?
    var follow_up_actions: [String]?
    var summary: String?
}

// MARK: - Content View

struct ContentView: View {
    @State private var isRecording = false
    @State private var currentText = ""
    @State private var segments: [SpeechSegment] = []
    @State private var statusMessage = "Pronto para gravar"
    @State private var segmentCount = 0
    @State private var showEnrollmentSheet = false
    @State private var isEnrolled = false
    @State private var isRestartingRecognition = false

    // ── LLM ──
    @State private var isProcessingLLM = false
    @State private var crmProfile: CRMProfile? = nil
    @State private var showCRMSheet = false

    @State private var consultantEnrollmentSamples16k: [Float] = []

    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "pt-PT"))
    private let audioEngine = AVAudioEngine()

    @State private var diarizer = DiarizerManager()

    @State private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    @State private var recognitionTask: SFSpeechRecognitionTask?
    @State private var silenceTimer: Timer?
    @State private var lastTextChange = Date()
    @State private var diarizationTimer: Timer?

    private let silenceThreshold: TimeInterval = 1
    private let backendURL = "http://192.168.1.87:5003"

    @State private var recordingSampleRate: Double = 16000
    @State private var currentSegmentSamples: [Float] = []
    @State private var allAudioSamples: [Float] = []

    var body: some View {
        NavigationView {
            ZStack {
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
                                        SegmentView(segment: segment).id(segment.id)
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

                // ── Loading overlay ──
                if isProcessingLLM {
                    Color.black.opacity(0.4).ignoresSafeArea()
                    VStack(spacing: 20) {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .scaleEffect(1.5)
                        Text("A analisar conversa com IA...")
                            .foregroundColor(.white)
                            .font(.headline)
                        Text("A extrair dados para o CRM...")
                            .foregroundColor(.white.opacity(0.8))
                            .font(.caption)
                    }
                    .padding(40)
                    .background(Color(.systemGray2).opacity(0.9))
                    .cornerRadius(20)
                }
            }
            .navigationTitle("Voice CRM")
            .navigationBarTitleDisplayMode(.large)
            .sheet(isPresented: $showEnrollmentSheet) {
                EnrollmentView(
                    isEnrolled: $isEnrolled,
                    consultantEnrollmentSamples16k: $consultantEnrollmentSamples16k
                )
            }
            .sheet(isPresented: $showCRMSheet) {
                if let profile = crmProfile {
                    CRMResultView(profile: profile)
                }
            }
        }
        .onAppear { requestPermissions() }
    }

    private var enrollmentHeader: some View {
        Group {
            if !isEnrolled {
                Button { showEnrollmentSheet = true } label: {
                    HStack {
                        Image(systemName: "person.crop.circle.badge.plus")
                        Text("Fazer enrolamento do consultor").bold()
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
                    Image(systemName: "checkmark.circle.fill").foregroundColor(.green)
                    Text("Consultor identificado").foregroundColor(.green).font(.caption).bold()
                    Spacer()
                    if crmProfile != nil {
                        Button("Ver CRM") { showCRMSheet = true }
                            .font(.caption).foregroundColor(.blue)
                    }
                    Button("Refazer") {
                        isEnrolled = false
                        consultantEnrollmentSamples16k = []
                        crmProfile = nil
                        showEnrollmentSheet = true
                    }
                    .font(.caption).foregroundColor(.orange)
                }
                .padding(.horizontal)
            }
        }
    }

    private var controls: some View {
        HStack(spacing: 20) {
            Button {
                if isRecording { stopRecording() } else {
                    allAudioSamples = []
                    currentSegmentSamples = []
                    startRecording()
                }
            } label: {
                Text(isRecording ? "⏹ Parar" : "🎙 Iniciar")
                    .font(.title2).bold().foregroundColor(.white)
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
                    crmProfile = nil
                } label: {
                    Text("🗑 Limpar")
                        .font(.title2).foregroundColor(.white)
                        .frame(width: 120, height: 55)
                        .background(Color.gray).cornerRadius(28)
                }
            }
        }
        .padding(.bottom, 20)
    }

    // MARK: - LLM Extract

    func extractCRMData() async {
        guard !segments.isEmpty else { return }

        await MainActor.run { isProcessingLLM = true }

        let segmentsPayload = segments.map { seg in
            ["speaker": seg.speaker, "text": seg.text, "timestamp": seg.timeString]
        }

        guard let url = URL(string: "\(backendURL)/extract") else { return }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 60

        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: ["segments": segmentsPayload])
            let (data, _) = try await URLSession.shared.data(for: request)
            
    
            if let profile = try? JSONDecoder().decode(CRMProfile.self, from: data) {
                await MainActor.run {
                    crmProfile = profile
                    isProcessingLLM = false
                    showCRMSheet = true
                    statusMessage = "Análise CRM concluída ✅"
                }
                return
            }
      
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let raw = json["raw"] as? String,
               let rawData = raw.data(using: .utf8),
               let profile = try? JSONDecoder().decode(CRMProfile.self, from: rawData) {
                await MainActor.run {
                    crmProfile = profile
                    isProcessingLLM = false
                    showCRMSheet = true
                    statusMessage = "Análise CRM concluída ✅"
                }
                return
            }
            
            await MainActor.run {
                isProcessingLLM = false
                statusMessage = "Erro: resposta inesperada do servidor"
            }
        } catch {
            await MainActor.run {
                isProcessingLLM = false
                statusMessage = "Erro na análise: \(error.localizedDescription)"
            }
        }
    }

    // MARK: - Permissions

    func requestPermissions() {
        SFSpeechRecognizer.requestAuthorization { status in
            DispatchQueue.main.async {
                statusMessage = status == .authorized ? "Pronto para gravar" : "Permissão de fala negada"
            }
        }
        AVAudioApplication.requestRecordPermission { granted in
            DispatchQueue.main.async {
                if !granted { statusMessage = "Permissão de microfone negada" }
            }
        }
    }

    // MARK: - Recording

    func startRecording() {
        recognitionTask?.cancel()
        recognitionTask = nil
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.record, mode: .measurement, options: .duckOthers)
            try session.setActive(true, options: .notifyOthersOnDeactivation)
        } catch { statusMessage = "Erro ao ativar áudio"; return }

        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest else { return }
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
                if nsError.domain == "kLSRErrorDomain", nsError.code == 301 { return }
                if nsError.domain == "kAFAssistantErrorDomain", nsError.code == 1110 {
                    DispatchQueue.main.async { self.statusMessage = "À espera de fala..." }
                    self.restartRecognition(after: 2.0); return
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
        } catch { statusMessage = "Erro ao iniciar microfone"; return }

        isRecording = true
        currentText = ""
        lastTextChange = Date()
        statusMessage = "A gravar..."
        startSilenceTimer()
        startDiarizationTimer()
    }

    func stopRecording() {
        silenceTimer?.invalidate(); silenceTimer = nil
        diarizationTimer?.invalidate(); diarizationTimer = nil
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
            statusMessage = "Gravação terminada — falta enrolamento do consultor"; return
        }

        let conversationSamples16k = resampleTo16k(samples: allAudioSamples, fromRate: recordingSampleRate)
        statusMessage = "A processar diarização..."

        Task {
            await diarizeAndUpdateSegments(conversationSamples16k: conversationSamples16k)
            await extractCRMData()
        }
    }

    func startDiarizationTimer() {
        diarizationTimer?.invalidate()
        diarizationTimer = Timer.scheduledTimer(withTimeInterval: 8.0, repeats: true) { _ in
            guard self.isEnrolled, !self.consultantEnrollmentSamples16k.isEmpty else { return }
            let samples = self.resampleTo16k(samples: self.allAudioSamples, fromRate: self.recordingSampleRate)
            guard samples.count > 16000 * 3 else { return }
            Task { await self.diarizeAndUpdateSegments(conversationSamples16k: samples) }
        }
    }

    func restartRecognition(after delay: TimeInterval = 0.05) {
        guard isRecording, !isRestartingRecognition else { return }
        isRestartingRecognition = true
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
        recognitionRequest = nil
        recognitionTask = nil
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
            self.isRestartingRecognition = false
            if self.isRecording { self.startRecording() }
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
        guard !text.isEmpty else { return }
        let endTime = Double(allAudioSamples.count) / recordingSampleRate
        let duration = Double(currentSegmentSamples.count) / recordingSampleRate
        let startTime = max(0, endTime - duration)
        segmentCount += 1
        segments.append(SpeechSegment(index: segmentCount, text: text, timestamp: Date(), startTime: startTime, endTime: endTime, speaker: "A identificar..."))
        currentSegmentSamples = []
        currentText = ""
        statusMessage = "Segmento \(segmentCount)"
        if shouldRestartRecognition, isRecording { restartRecognition() }
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
            let consultantSpeakerId = dominantSpeakerId(in: result.segments, from: enrollmentStart, to: enrollmentEnd, speakerId: { String($0.speakerId) }, startTime: { Double($0.startTimeSeconds) }, endTime: { Double($0.endTimeSeconds) })
            await MainActor.run {
                guard let consultantSpeakerId else { statusMessage = "Não consegui identificar o consultor"; return }
                for index in segments.indices {
                    let segmentStart = segments[index].startTime + conversationOffset
                    let segmentEnd = segments[index].endTime + conversationOffset
                    let speakerId = dominantSpeakerId(in: result.segments, from: segmentStart, to: segmentEnd, speakerId: { String($0.speakerId) }, startTime: { Double($0.startTimeSeconds) }, endTime: { Double($0.endTimeSeconds) })
                    segments[index].speaker = speakerId == consultantSpeakerId ? "Consultor" : "Cliente"
                }
                statusMessage = "Diarização concluída — a analisar com IA..."
            }
        } catch {
            await MainActor.run { statusMessage = "Erro na diarização: \(error.localizedDescription)" }
        }
    }

    func dominantSpeakerId<Segment>(in diarizationSegments: [Segment], from start: Double, to end: Double, speakerId: (Segment) -> String, startTime: (Segment) -> Double, endTime: (Segment) -> Double) -> String? {
        var scores: [String: Double] = [:]
        for segment in diarizationSegments {
            let overlap = min(end, endTime(segment)) - max(start, startTime(segment))
            if overlap > 0 { scores[speakerId(segment), default: 0] += overlap }
        }
        return scores.max(by: { $0.value < $1.value })?.key
    }

    func resampleTo16k(samples: [Float], fromRate: Double) -> [Float] {
        guard !samples.isEmpty, abs(fromRate - 16000) >= 1 else { return samples }
        let ratio = 16000.0 / fromRate
        let outputCount = Int(Double(samples.count) * ratio)
        guard outputCount > 0 else { return [] }
        var output = [Float](repeating: 0, count: outputCount)
        for i in 0..<outputCount {
            let sourceIndex = Double(i) / ratio
            let low = Int(sourceIndex)
            let high = min(low + 1, samples.count - 1)
            output[i] = samples[low] * (1 - Float(sourceIndex - Double(low))) + samples[high] * Float(sourceIndex - Double(low))
        }
        return output
    }
}

// MARK: - CRM Result View

struct CRMResultView: View {
    let profile: CRMProfile
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {

                    if let summary = profile.summary, !summary.isEmpty {
                        CRMSection(title: "📋 Resumo") {
                            Text(summary).font(.body)
                        }
                    }

                    if let cp = profile.client_profile {
                        CRMSection(title: "👤 Perfil do Cliente") {
                            CRMRow(label: "Género", value: cp.gender)
                            CRMRow(label: "Faixa etária", value: cp.age_range)
                            CRMRow(label: "Residência", value: cp.residence)
                            CRMRow(label: "Tier", value: cp.client_tier)
                            CRMRow(label: "Preferências de estilo", value: cp.style_preferences?.joined(separator: ", "))
                            CRMRow(label: "Tecidos preferidos", value: cp.fabric_preferences?.joined(separator: ", "))
                            CRMRow(label: "Tamanho roupa", value: cp.sizes?.clothing)
                            CRMRow(label: "Tamanho calçado", value: cp.sizes?.shoes)
                        }
                    }

                    if let cv = profile.current_visit {
                        CRMSection(title: "🛍 Visita Atual") {
                            CRMRow(label: "Produtos mencionados", value: cv.products_mentioned?.joined(separator: ", "))
                            CRMRow(label: "Intenção de compra", value: cv.purchase_intent)
                            CRMRow(label: "Orçamento", value: cv.budget_range)
                            CRMRow(label: "Ocasião", value: cv.occasion)
                        }
                    }

                    if let ph = profile.purchase_history {
                        CRMSection(title: "🕑 Histórico") {
                            CRMRow(label: "Produtos possuídos", value: ph.products_owned?.joined(separator: ", "))
                            CRMRow(label: "Gasto estimado", value: ph.estimated_spend)
                            CRMRow(label: "Frequência de compra", value: ph.purchase_frequency)
                        }
                    }

                    if let relations = profile.family_relations, !relations.isEmpty {
                        CRMSection(title: "👨‍👩‍👧 Relações Familiares") {
                            ForEach(Array(relations.enumerated()), id: \.offset) { _, rel in
                                VStack(alignment: .leading, spacing: 4) {
                                    CRMRow(label: "Relação", value: rel.relation)
                                    CRMRow(label: "Nome", value: rel.name)
                                    CRMRow(label: "Ocasiões", value: rel.occasions?.joined(separator: ", "))
                                    CRMRow(label: "Preferências", value: rel.preferences?.joined(separator: ", "))
                                }
                                .padding(.vertical, 4)
                                Divider()
                            }
                        }
                    }

                    if let memories = profile.memories, !memories.isEmpty {
                        CRMSection(title: "🧠 Memórias") {
                            ForEach(Array(memories.enumerated()), id: \.offset) { _, mem in
                                VStack(alignment: .leading, spacing: 2) {
                                    if let cat = mem.category, !cat.isEmpty {
                                        Text(cat.uppercased()).font(.caption2).foregroundColor(.orange).bold()
                                    }
                                    if let content = mem.content, !content.isEmpty {
                                        Text(content).font(.body)
                                    }
                                }
                                .padding(.vertical, 4)
                                Divider()
                            }
                        }
                    }

                    if let actions = profile.follow_up_actions, !actions.isEmpty {
                        CRMSection(title: "✅ Próximas Ações") {
                            ForEach(actions, id: \.self) { action in
                                HStack(alignment: .top) {
                                    Text("•").foregroundColor(.blue)
                                    Text(action)
                                }
                            }
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Dados CRM")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Fechar") { dismiss() }
                }
            }
        }
    }
}

struct CRMSection<Content: View>: View {
    let title: String
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title).font(.headline).bold()
            VStack(alignment: .leading, spacing: 6) { content }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(10)
        }
    }
}

struct CRMRow: View {
    let label: String
    let value: String?

    var body: some View {
        if let value, !value.isEmpty {
            HStack(alignment: .top) {
                Text(label).font(.caption).foregroundColor(.gray).frame(width: 130, alignment: .leading)
                Text(value).font(.body).frame(maxWidth: .infinity, alignment: .leading)
            }
        }
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
            Text("Enrolamento do Consultor").font(.title2).bold()
            Text(statusText).multilineTextAlignment(.center).foregroundColor(.gray).padding(.horizontal)
            if isRecording {
                Text("\(countdown)").font(.system(size: 80, weight: .bold)).foregroundColor(.red)
            }
            Button { if !isRecording { startEnrollment() } } label: {
                Text(isRecording ? "A gravar..." : "🎙 Iniciar Enrolamento")
                    .font(.title3).bold().foregroundColor(.white)
                    .frame(width: 250, height: 55)
                    .background(isRecording ? Color.red : Color.orange)
                    .cornerRadius(28)
            }
            .disabled(isRecording)
            Button("Cancelar") { stopAudioOnly(); dismiss() }.foregroundColor(.gray)
        }
        .padding(40)
    }

    func startEnrollment() {
        enrollmentSamples = []; countdown = 10; isRecording = true
        statusText = "Fala normalmente durante 10 segundos..."
        let session = AVAudioSession.sharedInstance()
        try? session.setCategory(.record, mode: .measurement, options: .duckOthers)
        try? session.setActive(true, options: .notifyOthersOnDeactivation)
        let inputNode = audioEngine.inputNode
        let format = inputNode.outputFormat(forBus: 0)
        sampleRate = format.sampleRate
        inputNode.removeTap(onBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 4096, format: format) { buffer, _ in
            guard let data = buffer.floatChannelData else { return }
            let samples = Array(UnsafeBufferPointer(start: data[0], count: Int(buffer.frameLength)))
            DispatchQueue.main.async { self.enrollmentSamples.append(contentsOf: samples) }
        }
        try? audioEngine.start()
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            DispatchQueue.main.async {
                if self.countdown > 1 { self.countdown -= 1 } else { self.stopEnrollment() }
            }
        }
    }

    func stopEnrollment() {
        timer?.invalidate(); timer = nil
        audioEngine.stop(); audioEngine.inputNode.removeTap(onBus: 0)
        isRecording = false
        let resampled = resampleTo16k(samples: enrollmentSamples, fromRate: sampleRate)
        guard resampled.count >= 16000 * 3 else { statusText = "Enrolamento demasiado curto — tenta novamente"; return }
        consultantEnrollmentSamples16k = resampled
        isEnrolled = true
        statusText = "Enrolamento concluído"
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { dismiss() }
    }

    func stopAudioOnly() {
        timer?.invalidate(); timer = nil
        if audioEngine.isRunning { audioEngine.stop(); audioEngine.inputNode.removeTap(onBus: 0) }
        isRecording = false
    }

    func resampleTo16k(samples: [Float], fromRate: Double) -> [Float] {
        guard !samples.isEmpty, abs(fromRate - 16000) >= 1 else { return samples }
        let ratio = 16000.0 / fromRate
        let outputCount = Int(Double(samples.count) * ratio)
        guard outputCount > 0 else { return [] }
        var output = [Float](repeating: 0, count: outputCount)
        for i in 0..<outputCount {
            let sourceIndex = Double(i) / ratio
            let low = Int(sourceIndex)
            let high = min(low + 1, samples.count - 1)
            output[i] = samples[low] * (1 - Float(sourceIndex - Double(low))) + samples[high] * Float(sourceIndex - Double(low))
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
        let f = DateFormatter(); f.dateFormat = "HH:mm:ss"; return f.string(from: timestamp)
    }
}

// MARK: - Segment View

struct SegmentView: View {
    let segment: SpeechSegment
    var speakerColor: Color {
        segment.speaker == "Consultor" ? .blue : segment.speaker == "Cliente" ? .green : .orange
    }
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text("\(segment.index)").font(.caption).bold().foregroundColor(.white)
                .frame(width: 28, height: 28).background(speakerColor).clipShape(Circle())
            VStack(alignment: .leading, spacing: 4) {
                Text(segment.speaker).font(.caption).bold().foregroundStyle(speakerColor)
                Text(segment.text).font(.body).frame(maxWidth: .infinity, alignment: .leading)
                Text(segment.timeString).font(.caption2).foregroundColor(.gray)
            }
        }
        .padding(12).background(Color(.systemGray6)).cornerRadius(10)
    }
}

#Preview { ContentView() }
