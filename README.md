# <center> Reminder System v1.0-beta: <br> READ ME

## About the App
The **Reminder System** is a high-density task manager designed for 
the "calendrically challenged" (people who don't look at their
calendar, because they are generally "sparse", without much in them).

Unlike traditional calendars that rely on static dates in a large matrix,
this system maintains an easily-viewed **List** of Reminders, prioritizing
**Visual Urgency** with dynamic countdowns and a "half-life" alert 
philosophy to ensure critical events are never missed.

If you're the sort of person that tends to maintain a *list* of upcoming
activites in addition to (or instead of) a calendar, this app is for you.

### Core Design Goals
* **Time-Remaining Focus:** Display exactly how much time remains
  (e.g., 2 weeks, 3 days, 10 min) rather than just a raw date.
* **Flexible Scheduling:** Full support for repeated events, "Date TBD" entries, and automated "half-life" reminders.
* **High-Density UI:** A "snug-fit" layout that maximizes information density without sacrificing readability.

### Current Features (v1.0-beta)
* **Visual Countdowns:** See "2 weeks" or "10 min" remaining, rather 
  than just a static date.
* **Dynamic Sorting:** Reminders are always sorted; "TBD" items 
  without a date automatically float to the top for visibility.
* **Day/Date Feedback:** Keep day and date in sync during data entry,
  echo those values to the user to help prevent scheduling errors.
* **Flexible Dates:** Full support for "Date or Time TBD" reminders,  
  along with manual editing/erasing of dates and times.
* **Standardized Storage:** Data files are stored in the user's standard 
  application-data folder.
* **Atomic Saves:** Data is saved after every change. If your system 
  crashes, you lose the last action at most, never the database.

### Coming Soon (High Priority)
* **Automated "Half-Life" Alerts:** Escalating reminders that 
  intensify as an event approaches.
* **Repeat Events:** Support for daily, weekly, and custom recurring 
  reminders.

## Installation & Setup

### **1. Clone the repository:**
   ```bash
   git clone https://github.com
   cd YOUR_REPO_NAME```
```
### **2. Install the requirements:**  
   ```bash
    pip install -r requirements.txt``
```
### **3. Run the application:**
    ```bash
    python app/main.py


## Documentation
 * [Quick Start](docs/QuickStart.md) - 60-second intro
 * [User Guide](docs/UserGuide.md) - Detailed philosophy & "How to"
 * [Design Notes](docs/DesignNotes.md) - — Technical details