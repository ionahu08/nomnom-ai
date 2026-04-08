import SwiftUI

struct DiaryView: View {
    @StateObject private var viewModel = DiaryViewModel()

    var body: some View {
        NavigationStack {
            ZStack {
                NomNomColors.background.ignoresSafeArea()

                VStack {
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

                    ScrollViewReader { proxy in
                        ScrollView {
                            VStack(spacing: 24) {
                                // Calendar months
                                if viewModel.isLoadingCalendar {
                                    ProgressView()
                                        .tint(NomNomColors.primary)
                                } else {
                                    calendarMonths
                                }

                                Divider()
                                    .padding(.vertical, 16)

                                // Logs for selected date
                                logsSection
                            }
                            .padding(.vertical, 16)
                        }
                        .onAppear {
                            // Jump to selected date on load
                            proxy.scrollTo(viewModel.selectedDate, anchor: .top)
                        }
                    }
                }
            }
            .navigationTitle("Food Diary")
            .navigationBarTitleDisplayMode(.inline)
            .toolbarColorScheme(.dark, for: .navigationBar)
            .task {
                await viewModel.loadCalendarSummary()
            }
        }
    }

    // MARK: - Calendar Months

    private var calendarMonths: some View {
        let calendar = Calendar.current
        let startDate = calendar.date(from: DateComponents(year: 2026, month: 1, day: 1))!

        let now = Date()
        let endComponents = calendar.dateComponents([.year, .month], from: now)
        var nextMonthComponents = endComponents
        nextMonthComponents.month! += 1
        if nextMonthComponents.month! > 12 {
            nextMonthComponents.month! = 1
            nextMonthComponents.year! += 1
        }
        nextMonthComponents.day = 1
        let endDate = calendar.date(from: nextMonthComponents)!

        var months: [Date] = []
        var currentMonth = startDate
        while currentMonth < endDate {
            months.append(currentMonth)
            currentMonth = calendar.date(byAdding: .month, value: 1, to: currentMonth)!
        }

        return VStack(spacing: 24) {
            ForEach(months, id: \.self) { month in
                MonthCalendarView(
                    month: month,
                    summary: viewModel.calendarSummary,
                    selectedDate: viewModel.selectedDate,
                    onDateTap: { date in
                        viewModel.selectedDate = date
                        Task {
                            await viewModel.loadLogs(for: date)
                        }
                    }
                )
            }
        }
        .padding(.horizontal, 16)
    }

    // MARK: - Logs Section

    private var logsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Date header
            Text(formatDateDisplay(viewModel.selectedDate))
                .font(.headline)
                .foregroundColor(NomNomColors.textPrimary)
                .padding(.horizontal, 16)

            if viewModel.isLoadingLogs {
                ProgressView()
                    .tint(NomNomColors.primary)
            } else if viewModel.logsForSelectedDate.isEmpty {
                VStack(spacing: 8) {
                    Text("No food logged")
                        .font(.subheadline)
                        .foregroundColor(NomNomColors.textSecondary)
                }
                .frame(maxWidth: .infinity)
                .padding()
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
        let monthName = formatMonthYear(month)
        let daysInMonth = calendar.range(of: .day, in: .month, for: month)?.count ?? 0
        let firstDay = calendar.date(from: calendar.dateComponents([.year, .month], from: month))!
        let firstWeekday = calendar.component(.weekday, from: firstDay) - 1 // 0=Sunday

        return VStack(alignment: .leading, spacing: 12) {
            Text(monthName)
                .font(.headline)
                .foregroundColor(NomNomColors.textPrimary)

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
        .background(NomNomColors.surface)
        .cornerRadius(12)
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
            .background(isSelected ? NomNomColors.primary : NomNomColors.background)
            .cornerRadius(8)
        }
    }

    private func formatDateISO(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: date)
    }
}

// MARK: - Async Photo Thumbnail

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
        isLoading = true

        do {
            let filename = photoPath.split(separator: "/").last.map(String.init) ?? photoPath
            let data = try await APIClient.shared.getData(path: "/api/v1/photos/\(filename)")
            if let uiImage = UIImage(data: data) {
                self.image = uiImage
            }
        } catch {
            // Silently fail, show placeholder
        }

        isLoading = false
    }
}
