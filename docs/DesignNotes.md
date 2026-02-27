
# <center> Reminder System v1.0-beta: <br> DESIGN NOTES

## Development & IDE Notes
PyCharm's "Unresolved attribute reference" inspection is disabled for 
this project, to prevent bogus warnings from PyCharm's static analyzer.

Reason:
Qt injects attributes dynamically from C++. As a result, PyCharm's 
static analyzer cannot see:
- Qt.DisplayRole
- Qt.AlignCenter
- Qt.ItemIsEnabled
- etc.

These references cannot be validated by PyCharm's static type engine.
So they MUST be validated by unit tests.

(Re-enable this inspection if/when PyCharm fixes its Qt stubs.)

## Architecture & Design
# <center> Reminder System v1.0-beta: <br> ARCHITECTURE & DESIGN NOTES

## Development & IDE Notes
### PyCharm Static Analysis
PyCharm's "Unresolved attribute reference" inspection is **disabled** 
for this project.
*   **Reason:** [Qt for Python](https://doc.qt.io) injects many attributes
   *dynamically* from C++. (`Qt.DisplayRole`, `Qt.AlignCenter`, etc)
*   **Validation:** Because the [PyCharm Static Analysis](https://www.jetbrains.com) 
    engine cannot see these attributes, UI logic must be validated via manual testing or the unit test suite.
*   **Re-enable** this inspection if/when JetBrains improves Qt stub support.

# Architecture & DesignNotes

### The Model/View Paradigm
This project utilizes the [Qt Model/View Framework](https://doc.qt.io) to decouple data from its presentation. 
*   **The View:** A `QTableView` is the lens through which users 
    interact with the data.
*   **The View's "Model":** A `QAbstractTableModel` instance is actually
    a thin pass-thru delegation layer for the *domain model*.
*   **The Domain Model:** the "Single Source of Truth" for the app is 
    the RemindersModel instance, which manages the list of domain data 
    objects (ReminderItems).

### UI Management
*   **UI Delegates:**  
    Custom extensions of [QAbstractItemDelegate](https://doc.qt.io)
    handle the painting of data cells, replacing the need for individual
    widgets in every row. With that approach, low-level [QPainter](https://doc.qt.io) 
    objects draw the data cells. 
    * **Performance:**  
       Drawing text and icons directly during the
        `paint()` event, avoids the overhead of thousands of sub-widgets, 
         keeping the UI responsive.
    *   **"Governor" Logic:** The delegate enforces a `line_limit` to ensure rows stay "snug." If a description exceeds this limit, the painter manually calculates the clip and appends an elide indicator (`...`).
    *   **Bold/Center Logic:** Critical items trigger a font-weight shift. The delegate manually calculates the vertical center to prevent "line-ghosting" where only the middle of a multi-line string appears.


* **Row-Height Dynamics:**  
Row heights are calculated dynamically based on the **Description** 
column content. 
  *   **Snug-Fit:** The view uses `ResizeToContents` for the initial load, then switches to `Interactive` mode to allow user adjustments.
  *   **Vertical Gravity:** If a row expands for multiple lines, the **Countdown** and **Date** columns are anchored to the top to maintain visual alignment with the start of the description.
