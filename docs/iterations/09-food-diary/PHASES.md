# Phases — Food Diary (Iteration 09)

## Phase 1: Backend Service Functions

**File:** `NomNom-Backend/src/services/food_log_service.py`

### list_logs_for_date(db, user_id, date)

```python
async def list_logs_for_date(
    db: AsyncSession, user_id: int, date: date_type
) -> list[FoodLog]:
    """Fetch all logs for a specific date (midnight UTC boundaries)."""
    day_start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)
    result = await db.execute(
        select(FoodLog)
        .where(
            FoodLog.user_id == user_id,
            FoodLog.logged_at >= day_start,
            FoodLog.logged_at < day_end,
        )
        .order_by(FoodLog.logged_at.asc())
    )
    return list(result.scalars().all())
```

Keep `list_today_logs` as a thin wrapper: `return await list_logs_for_date(db, user_id, date.today())`

### list_calendar_summary(db, user_id, start, end)

```python
async def list_calendar_summary(
    db: AsyncSession, user_id: int, start: date_type, end: date_type
) -> list[dict]:
    """Per-day aggregation: count + first 3 photo filenames."""
    # Query: GROUP BY date(logged_at), aggregate count + photo_paths
    # Return: [{date: "2026-04-08", count: 2, photo_paths: ["abc.jpg", "def.jpg"]}, ...]
```

---

## Phase 2: Backend Schemas

**File:** `NomNom-Backend/src/schemas/food_log.py`

Add new schema:

```python
class DayCalendarSummary(BaseModel):
    """Summary for a calendar day."""
    date: str                # "YYYY-MM-DD"
    count: int              # number of logs that day
    photo_paths: list[str]  # first 3 photo filenames for badges
```

---

## Phase 3: Backend API Endpoints

**File:** `NomNom-Backend/src/api/food_logs.py`

### GET /by-date

```python
@router.get("/by-date", response_model=list[FoodLogResponse])
async def get_logs_by_date(
    date: str,  # query param: "YYYY-MM-DD"
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch all logs for a specific date."""
    try:
        target_date = date_type.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    logs = await list_logs_for_date(db, current_user.id, target_date)
    return logs
```

### GET /calendar-summary

```python
@router.get("/calendar-summary", response_model=list[DayCalendarSummary])
async def get_calendar_summary(
    start: str,  # "YYYY-MM-DD"
    end: str,    # "YYYY-MM-DD"
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch calendar summary for a date range."""
    try:
        start_date = date_type.fromisoformat(start)
        end_date = date_type.fromisoformat(end)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    summary = await list_calendar_summary(db, current_user.id, start_date, end_date)
    return summary
```

---

## Phase 4: iOS Models

**File:** `NomNom-iOS/NomNom/Core/Models/FoodLog.swift`

Add struct:

```swift
struct DayCalendarSummary: Codable, Identifiable {
    var id: String { date }
    let date: String        // "YYYY-MM-DD"
    let count: Int
    let photoPaths: [String]

    enum CodingKeys: String, CodingKey {
        case date
        case count
        case photoPaths = "photo_paths"
    }
}
```

---

## Phase 5: iOS ViewModel

**File:** `NomNom-iOS/NomNom/Features/Diary/DiaryViewModel.swift` (NEW)

```swift
@MainActor
class DiaryViewModel: ObservableObject {
    @Published var selectedDate: Date = Date()
    @Published var logsForSelectedDate: [FoodLogResponse] = []
    @Published var calendarSummary: [DayCalendarSummary] = []
    @Published var isLoadingLogs = false
    @Published var isLoadingCalendar = false
    @Published var errorMessage: String?

    func loadCalendarSummary() async {
        // Fetch Jan 2026 → first day of next month
        // Parse API response, set selectedDate to last date with logs
    }

    func loadLogs(for date: Date) async {
        // Fetch logs for date via /by-date endpoint
    }

    func deleteLog(id: Int) async {
        // Delete via API, reload calendar summary to update badges
    }
}
```

---

## Phase 6: iOS View

**File:** `NomNom-iOS/NomNom/Features/Diary/DiaryView.swift` (NEW)

**Structure:**

```
NavigationStack
  ↓ (error banner if errorMessage is set)
  ↓ (loading spinner if isLoadingCalendar)
  ScrollViewReader(proxy)
    ScrollView
      VStack(spacing: 24)
        ForEach months (Jan 2026 → current):
          MonthCalendarView(month, summary, selectedDate, onDateTap)
        
        Divider
        
        logsSection:
          Text("April 8, 2026")
          todaySummaryCard(cals, protein, carbs, fat)
          if isLoadingLogs:
            ProgressView()
          else if logs.isEmpty:
            Text("No food logged")
          else:
            ForEach logs:
              Text(formatTime(log.loggedAt))
              FoodLogCard(log)
              .swipeActions { Button("Delete", role: .destructive) }
```

**MonthCalendarView:** 7-column grid showing month name + day cells

**DayCell:** day number + optional photo badge, highlight if selected, accent dot if today

**AsyncPhotoThumbnail:** Lazy loads photo from API via getData()

---

## Phase 7: Navigation

**File:** `NomNom-iOS/NomNom/App/ContentView.swift`

Replace:
```swift
TodayView()
    .tabItem { Image(systemName: "list.bullet"); Text("Today") }
```

With:
```swift
DiaryView()
    .tabItem { Image(systemName: "calendar"); Text("Food Diary") }
```

**Delete:**
- `NomNom-iOS/NomNom/Features/Dashboard/TodayView.swift`
- `NomNom-iOS/NomNom/Features/Dashboard/TodayViewModel.swift`

---

## Testing

### Backend

- POST food log, then GET /by-date for that date → verify log appears
- POST multiple logs on same day, verify calendar-summary count
- GET /by-date with invalid format → 400 error
- GET /by-date without auth → 401 error

### iOS

- Calendar renders all months
- Photo badges appear for logged days
- Tap date → logs section updates
- Swipe-to-delete → log removed + calendar badge updates
- App opens to last logged date

---

## Reuse

- `FoodLogCard` — unchanged, reused as-is in logs section
- `APIClient.shared.get()` and `getData()` — unchanged
- `NomNomColors` palette — same throughout
- Swipe-to-delete pattern — replicated from TodayView
