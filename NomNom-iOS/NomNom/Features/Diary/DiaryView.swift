import SwiftUI

struct DiaryView: View {
    @StateObject private var viewModel = DiaryViewModel()
    @State private var displayedMonth: Date = Date()
    @State private var showYearPicker = false
    @State private var swipeDirection: Edge = .trailing

    var body: some View {
        NavigationStack {
            ZStack {
                LinearGradient(
                    colors: [
                        Color(red: 0.09, green: 0.07, blue: 0.13),
                        Color(red: 0.14, green: 0.09, blue: 0.07),
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()

                VStack(spacing: 0) {
                    // Error banner
                    if let error = viewModel.errorMessage {
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(NomNomColors.danger)
                            Text(error)
                                .font(.caption)
                                .foregroundColor(NomNomColors.danger)
                            Spacer()
                            Button(action: { viewModel.errorMessage = nil }) {
                                Image(systemName: "xmark")
                                    .foregroundColor(NomNomColors.danger)
                            }
                        }
                        .padding()
                        .background(NomNomColors.danger.opacity(0.1))
                        .cornerRadius(8)
                        .padding(16)
                    }

                    ScrollView {
                        VStack(spacing: 16) {
                            // Month/year navigation header
                            HStack {
                                Button(action: { withAnimation(.easeInOut(duration: 0.3)) {
                                    swipeDirection = .trailing
                                    goToPreviousMonth()
                                }}) {
                                    Image(systemName: "chevron.left")
                                        .foregroundColor(NomNomColors.primary)
                                        .font(.system(size: 16, weight: .semibold))
                                }

                                Spacer()

                                Button(action: { showYearPicker = true }) {
                                    HStack(spacing: 4) {
                                        Text(formatMonthYear(displayedMonth))
                                            .font(.headline.weight(.semibold))
                                            .foregroundColor(NomNomColors.textPrimary)
                                        Image(systemName: "chevron.down.circle.fill")
                                            .font(.caption)
                                            .foregroundColor(NomNomColors.primary)
                                    }
                                }

                                Spacer()

                                Button(action: { withAnimation(.easeInOut(duration: 0.3)) {
                                    swipeDirection = .leading
                                    goToNextMonth()
                                }}) {
                                    Image(systemName: "chevron.right")
                                        .foregroundColor(NomNomColors.primary)
                                        .font(.system(size: 16, weight: .semibold))
                                }
                            }
                            .padding(.horizontal, 16)
                            .padding(.vertical, 12)

                            // Calendar for current month
                            if viewModel.isLoadingCalendar {
                                ProgressView()
                                    .tint(NomNomColors.primary)
                            } else {
                                MonthCalendarView(
                                    month: displayedMonth,
                                    summary: viewModel.calendarSummary,
                                    selectedDate: viewModel.selectedDate,
                                    onDateTap: { date in
                                        viewModel.selectedDate = date
                                        Task {
                                            await viewModel.loadLogs(for: date)
                                        }
                                    }
                                )
                                .id(displayedMonth)
                                .transition(.asymmetric(
                                    insertion: .move(edge: swipeDirection),
                                    removal: .move(edge: swipeDirection == .trailing ? .leading : .trailing)
                                ))
                                .gesture(
                                    DragGesture(minimumDistance: 40, coordinateSpace: .local)
                                        .onEnded { value in
                                            let h = value.translation.width
                                            let v = value.translation.height
                                            guard abs(h) > abs(v) else { return }
                                            withAnimation(.easeInOut(duration: 0.3)) {
                                                if h < 0 {
                                                    swipeDirection = .trailing
                                                    goToPreviousMonth()
                                                } else {
                                                    swipeDirection = .leading
                                                    goToNextMonth()
                                                }
                                            }
                                        }
                                )
                                .padding(.horizontal, 16)
                            }

                            Divider()
                                .padding(.vertical, 16)

                            // Logs for selected date
                            logsSection
                        }
                        .padding(.vertical, 16)
                    }
                }
            }
            .navigationTitle("🐾 Food Diary")
            .navigationBarTitleDisplayMode(.inline)
            .toolbarColorScheme(.dark, for: .navigationBar)
            .sheet(isPresented: $showYearPicker) {
                YearPickerSheet(
                    selectedYear: Calendar.current.component(.year, from: displayedMonth),
                    onSelect: { year in
                        var comps = Calendar.current.dateComponents([.year, .month], from: displayedMonth)
                        comps.year = year
                        displayedMonth = Calendar.current.date(from: comps) ?? displayedMonth
                        showYearPicker = false
                    }
                )
                .presentationDetents([.medium])
                .presentationDragIndicator(.visible)
            }
            .task {
                // Initialize displayedMonth to current month
                let calendar = Calendar.current
                let now = Date()
                let components = calendar.dateComponents([.year, .month], from: now)
                displayedMonth = calendar.date(from: DateComponents(year: components.year, month: components.month, day: 1)) ?? now

                await viewModel.loadCalendarSummary()
                // After calendar loads, load logs for the selected date
                await viewModel.loadLogs(for: viewModel.selectedDate)
            }
        }
    }

    // MARK: - Month Navigation

    private func goToPreviousMonth() {
        let calendar = Calendar.current
        displayedMonth = calendar.date(byAdding: .month, value: -1, to: displayedMonth) ?? displayedMonth
    }

    private func goToNextMonth() {
        let calendar = Calendar.current
        displayedMonth = calendar.date(byAdding: .month, value: 1, to: displayedMonth) ?? displayedMonth
    }

    // MARK: - Logs Section

    private var logsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Date header
            HStack(spacing: 6) {
                Image(systemName: "pawprint.fill")
                    .foregroundColor(NomNomColors.primary)
                    .font(.caption)
                Text(formatDateDisplay(viewModel.selectedDate))
                    .font(.headline)
                    .foregroundColor(NomNomColors.textPrimary)
            }
            .padding(.horizontal, 16)

            if viewModel.isLoadingLogs {
                ProgressView()
                    .tint(NomNomColors.primary)
            } else if viewModel.logsForSelectedDate.isEmpty {
                VStack(spacing: 10) {
                    Text("🐱")
                        .font(.system(size: 44))
                    Text("Nothing here yet")
                        .font(.subheadline.weight(.medium))
                        .foregroundColor(NomNomColors.textSecondary)
                    Text("The cat is judging your restraint")
                        .font(.caption)
                        .foregroundColor(NomNomColors.textSecondary.opacity(0.6))
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 24)
            } else {
                // Summary card
                todaySummary
                    .padding(.horizontal, 16)

                // Food logs
                VStack(spacing: 12) {
                    ForEach(viewModel.logsForSelectedDate) { log in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(formatTime(log.loggedAt))
                                .font(.caption)
                                .foregroundColor(NomNomColors.textSecondary)

                            FoodLogCard(log: log)
                                .swipeActions(edge: .trailing) {
                                    Button(role: .destructive) {
                                        Task { await viewModel.deleteLog(id: log.id) }
                                    } label: {
                                        Label("Delete", systemImage: "trash")
                                    }
                                }
                        }
                    }
                }
                .padding(.horizontal, 16)
            }
        }
    }

    private var todaySummary: some View {
        let totalCals = viewModel.logsForSelectedDate.reduce(0) { $0 + $1.calories }
        let totalProtein = viewModel.logsForSelectedDate.reduce(0.0) { $0 + $1.proteinG }
        let totalCarbs = viewModel.logsForSelectedDate.reduce(0.0) { $0 + $1.carbsG }
        let totalFat = viewModel.logsForSelectedDate.reduce(0.0) { $0 + $1.fatG }

        return VStack(spacing: 12) {
            HStack {
                Text("\(viewModel.logsForSelectedDate.count) meal\(viewModel.logsForSelectedDate.count == 1 ? "" : "s")")
                    .font(.subheadline)
                    .foregroundColor(NomNomColors.textSecondary)
                Spacer()
            }

            HStack(spacing: 16) {
                summaryItem(value: "\(totalCals)", label: "kcal", color: NomNomColors.primary)
                summaryItem(value: String(format: "%.0f", totalProtein), label: "protein", color: NomNomColors.success)
                summaryItem(value: String(format: "%.0f", totalCarbs), label: "carbs", color: NomNomColors.warning)
                summaryItem(value: String(format: "%.0f", totalFat), label: "fat", color: NomNomColors.danger)
            }
        }
        .padding()
        .background(NomNomColors.surface)
        .cornerRadius(16)
    }

    private func summaryItem(value: String, label: String, color: Color) -> some View {
        VStack(spacing: 2) {
            Text(value)
                .font(.headline)
                .foregroundColor(color)
            Text(label)
                .font(.caption2)
                .foregroundColor(NomNomColors.textSecondary)
        }
        .frame(maxWidth: .infinity)
    }

    // MARK: - Helpers

    private func formatDateDisplay(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMMM d, yyyy"
        return formatter.string(from: date)
    }

    private func formatMonthYear(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMMM yyyy"
        return formatter.string(from: date)
    }

    private func formatTime(_ isoString: String) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        guard let date = formatter.date(from: isoString) else { return isoString }

        let timeFormatter = DateFormatter()
        timeFormatter.dateFormat = "h:mm a"
        return timeFormatter.string(from: date)
    }
}

// MARK: - Month Calendar View

struct MonthCalendarView: View {
    let month: Date
    let summary: [DayCalendarSummary]
    let selectedDate: Date
    let onDateTap: (Date) -> Void

    var body: some View {
        let calendar = Calendar.current
        let daysInMonth = calendar.range(of: .day, in: .month, for: month)?.count ?? 0
        let firstDay = calendar.date(from: calendar.dateComponents([.year, .month], from: month))!
        let firstWeekday = calendar.component(.weekday, from: firstDay) - 1 // 0=Sunday

        return VStack(alignment: .leading, spacing: 16) {
            // Weekday headers
            let weekdays = ["S", "M", "T", "W", "T", "F", "S"]
            HStack {
                ForEach(Array(weekdays.enumerated()), id: \.offset) { _, label in
                    Text(label)
                        .font(.caption2.weight(.semibold))
                        .foregroundColor(NomNomColors.textSecondary)
                        .frame(maxWidth: .infinity)
                }
            }

            // 7-column grid
            let columns = Array(repeating: GridItem(.flexible()), count: 7)
            LazyVGrid(columns: columns, spacing: 8) {
                // Empty cells for days before month starts
                ForEach(0..<firstWeekday, id: \.self) { _ in
                    Text("")
                }

                // Day cells
                ForEach(1...daysInMonth, id: \.self) { dayNum in
                    if let dayDate = calendar.date(byAdding: .day, value: dayNum - 1, to: firstDay) {
                        DayCell(
                            date: dayDate,
                            summary: summary,
                            selectedDate: selectedDate,
                            onTap: { onDateTap(dayDate) }
                        )
                    }
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color(red: 0.14, green: 0.11, blue: 0.18))
                .shadow(color: NomNomColors.primary.opacity(0.12), radius: 14, x: 0, y: 4)
        )
    }

    private func formatMonthYear(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMMM yyyy"
        return formatter.string(from: date)
    }
}

// MARK: - Day Cell

struct DayCell: View {
    let date: Date
    let summary: [DayCalendarSummary]
    let selectedDate: Date
    let onTap: () -> Void

    var body: some View {
        let calendar = Calendar.current
        let dateStr = formatDateISO(date)
        let dayData = summary.first { $0.date == dateStr }
        let isSelected = calendar.isDate(date, inSameDayAs: selectedDate)
        let isToday = calendar.isDateInToday(date)

        return Button(action: onTap) {
            VStack(spacing: 4) {
                Text("\(calendar.component(.day, from: date))")
                    .font(.subheadline.bold())
                    .foregroundColor(isSelected ? .white : NomNomColors.textPrimary)

                // Thumbnail badge
                if let photos = dayData?.photoPaths, !photos.isEmpty {
                    AsyncPhotoThumbnail(photoPath: photos[0])
                        .frame(width: 32, height: 32)
                        .cornerRadius(16)
                } else if isToday {
                    Circle()
                        .fill(NomNomColors.primary)
                        .frame(width: 6, height: 6)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 60)
            .background(
                isSelected
                    ? AnyView(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(NomNomColors.primary)
                            .shadow(color: NomNomColors.primary.opacity(0.5), radius: 6)
                      )
                    : AnyView(Color.clear)
            )
        }
    }

    private func formatDateISO(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: date)
    }
}

// MARK: - Async Photo Thumbnail

actor PhotoCache {
    static let shared = PhotoCache()
    private var cache: [String: UIImage] = [:]

    func image(for key: String) -> UIImage? {
        cache[key]
    }

    func setImage(_ image: UIImage, for key: String) {
        cache[key] = image
    }
}

struct AsyncPhotoThumbnail: View {
    let photoPath: String
    @State private var image: UIImage?
    @State private var isLoading = false

    var body: some View {
        Group {
            if let image = image {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFill()
            } else {
                Image(systemName: "photo")
                    .foregroundColor(NomNomColors.textSecondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(NomNomColors.surface)
            }
        }
        .task {
            await loadPhoto()
        }
    }

    private func loadPhoto() async {
        guard image == nil, !isLoading else { return }

        let filename = photoPath.split(separator: "/").last.map(String.init) ?? photoPath

        // Check cache first
        if let cachedImage = await PhotoCache.shared.image(for: filename) {
            self.image = cachedImage
            return
        }

        isLoading = true

        do {
            let data = try await APIClient.shared.getData(path: "/api/v1/photos/\(filename)")
            if let uiImage = UIImage(data: data) {
                await PhotoCache.shared.setImage(uiImage, for: filename)
                self.image = uiImage
            }
        } catch {
            // Silently fail, show placeholder
        }

        isLoading = false
    }
}

// MARK: - Year Picker Sheet

struct YearPickerSheet: View {
    let selectedYear: Int
    let onSelect: (Int) -> Void

    var years: [Int] { Array((2026...Calendar.current.component(.year, from: Date())).reversed()) }

    var body: some View {
        VStack(spacing: 0) {
            Text("🐾 Select Year")
                .font(.headline)
                .foregroundColor(NomNomColors.textPrimary)
                .padding()
            Divider().background(NomNomColors.textSecondary.opacity(0.3))
            ScrollView {
                VStack(spacing: 0) {
                    ForEach(years, id: \.self) { year in
                        Button(action: { onSelect(year) }) {
                            HStack {
                                Text(String(year))
                                    .font(.title3.weight(year == selectedYear ? .bold : .regular))
                                    .foregroundColor(year == selectedYear ? NomNomColors.primary : NomNomColors.textPrimary)
                                Spacer()
                                if year == selectedYear {
                                    Image(systemName: "pawprint.fill")
                                        .foregroundColor(NomNomColors.primary)
                                }
                            }
                            .padding(.horizontal, 24)
                            .padding(.vertical, 14)
                        }
                        Divider().background(NomNomColors.textSecondary.opacity(0.1))
                    }
                }
            }
        }
        .background(NomNomColors.background.ignoresSafeArea())
    }
}
