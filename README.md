# Half-Life Reminders App

# About the App
The intent is to create an easy-to-use, date-based reminder system for the 
calendrically challenged. (A club of which yours truly is a card-carrying member.)

## DESIGN GOALS
To that end, the idea is to:
* Entwr events, dates, and times in a simple, self-sorting list.
* Show how much time remains before an event (2 weeks, 3 days, 10 min, etc.)
Rather than just a date (which tends to be meaningless to those of us who
are calendarically-challended in the first place).
* Keep keep day and date in aync when entering an event, and echo that value, 
so we wont't create an event with one correct value and one wrong one. 
* Generate automated "half-life" alerts for upcoming events
* Handle repeated events
* Allow for undated (Date TBD) events

## Background & Motivation
People who refer to their calendars _frequently_, undoubtedly have what they
need already. But those of us who don't open a calendar regularly need a
somewhat different system. (A system like this one, it is hoped.)

The one time in my life calendars actually worked for me was back before
Windows had a "notification" system where a notification comes and then
disappears after a while---so you miss it unless you happen to be glued to
the screen and see it.

As someone who, on at least two occasions, showed up a week early for an event,
only to miss it the day of, the one and only infallible reminder system I ever
found was a series of "half-life" reminders.

That worked when I dialog came up that did _not go away_ until I closed it.
With those dialogs, I would start with a 4-week reminder for an event that
was far off. When I closed the reminder-alert, I changed the reminder time 
to 2 weeks. Then 1 week. Then 3 days. Then 1 day. Even down to 4-hr, 2-hr
reminders (etc.), down to 5 minutes before a meeting down the hall.

During the time I was using that system, I never once missed an event or
appointment---a feat for which I am certain I deserve a medal.

But with the advent of "notifications", my wonderful reminder system became
useless. Finally, after the umpteenth missed event, I decided to _build_ the
system I needed---and to take it one step further, with _automated_ "half life"
reminders.

That is the ultimate goal of this system (with a fair number of future additions
contemplated!).

# IMPLEMENTATION DETAILS
 * See **_PYCHARM_QT_INSPECTION_NOTE.txt** in the main folder

# DESIGN DETAILS

## Overview  
This application follows a lightweight **Model–View–Controller (MVC)** structure. The goal is to keep data, presentation, and interaction logic cleanly separated so each part can evolve independently. This makes the codebase teachable, debuggable, and easy to extend.

---

## Model Layer  
The **Model** represents the internal data structures and business logic.

### Components  
- **[Reminder](guide://action?prefill=Tell%20me%20more%20about%3A%20Reminder)**  
  - A pure data object: text, notes, and a `datetime` value.  
  - Contains no UI logic, formatting, or widget references.

- **[RemindersManager](guide://action?prefill=Tell%20me%20more%20about%3A%20RemindersManager)**  
  - Owns the list of `Reminder` objects.  
  - Handles loading, saving, sorting, adding, and deleting reminders.  
  - Acts as the single source of truth for application data.

### Responsibilities  
- Maintain internal state.  
- Provide clean APIs for data manipulation.  
- Remain UI‑agnostic.

---

## View Layer  
The **View** is responsible for presenting data to the user.

### Components  
- **[ReminderDisplay (Grid View)](guide://action?prefill=Tell%20me%20more%20about%3A%20ReminderDisplay%20(Grid%20View))**  
  - A wx.Grid subclass that displays reminders in rows and columns.  
  - Uses `populate()` to fill cells with text and attach buttons.  
  - Provides a `refresh()` method to redraw the grid when data changes.

- **[Formatting Module](guide://action?prefill=Tell%20me%20more%20about%3A%20Formatting%20Module)**  
  - Converts internal data into display‑ready strings.  
  - Applies date/time formats, combines text + notes, formats day‑of‑week.  
  - Keeps presentation logic out of the model and the grid.

### Responsibilities  
- Render data.  
- Contain all widget creation and layout.  
- Never modify the underlying data.

---

## Controller Layer  
The **Controller** coordinates interactions between the model and the view.

### Components  
- **[MainFrame](guide://action?prefill=Tell%20me%20more%20about%3A%20MainFrame)**  
  - Wires together the manager, data model, and grid.  
  - Handles user actions (Add, Edit, Delete, Exit).  
  - Calls `grid.refresh()` after any data change.

### Responsibilities  
- Respond to user events.  
- Update the model.  
- Tell the view when to refresh.  
- Contain no formatting logic and no data storage.

---

## Data Flow  
A reminder moves through the system like this:

1. **[RemindersManager](guide://action?prefill=Tell%20me%20more%20about%3A%20RemindersManager)** stores the raw `Reminder` objects.  
2. **[ReminderDataModel](guide://action?prefill=Tell%20me%20more%20about%3A%20ReminderDataModel)** adapts them into row/column values.  
3. **[Formatting](guide://action?prefill=Tell%20me%20more%20about%3A%20Formatting)** converts fields into display strings.  
4. **[ReminderDisplay](guide://action?prefill=Tell%20me%20more%20about%3A%20ReminderDisplay)** renders the grid and buttons.  
5. **[MainFrame](guide://action?prefill=Tell%20me%20more%20about%3A%20MainFrame)** handles user actions and triggers refreshes.

This keeps each layer focused on a single job.

---

## Why This Architecture  
- **[Testability](guide://action?prefill=Tell%20me%20more%20about%3A%20Testability)** — formatting and data logic can be tested without UI.  
- **[Maintainability](guide://action?prefill=Tell%20me%20more%20about%3A%20Maintainability)** — changes in one layer don’t break others.  
- **[Teachability](guide://action?prefill=Tell%20me%20more%20about%3A%20Teachability)** — each module has a clear purpose.  
- **[Extensibility](guide://action?prefill=Tell%20me%20more%20about%3A%20Extensibility)** — adding new columns or storage backends is straightforward.  
- **[UI Stability](guide://action?prefill=Tell%20me%20more%20about%3A%20UI%20Stability)** — the grid is dumb and predictable; the controller drives updates.

---

If you want, I can also generate a **README section diagram** (ASCII or Markdown) that visually shows the MVC flow and module relationships.