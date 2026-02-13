from app.model.reminders_model import RemindersModel
from .fixtures.reminder_factory import sample_reminders, sample_display_rows

# noinspection PyPep8Naming
import app.table_constants as C

def test_viewmodel_rows():
    reminders = sample_reminders()
    #TODO: Extract into a separate test for all rows
    # for r in reminders:
    #    print("WHEN TYPE:", type(r.when), r.when)
    vm = RemindersModel(reminder_list=reminders)   # No data manager for this test
    
    expected = sample_display_rows()
    actual = vm.display_rows()
    assert actual == expected
    
from tests.fixtures.mock_reminders import mock_reminders
def test_viewmodel_row_width():
    vm = RemindersModel(reminder_list=sample_reminders())
    for row in vm.display_rows():
        assert len(row) == len(C.VM_COLUMN_LABELS)

from app.qt_ui.model_adapter import ModelAdapter
def test_qt_adapter_column_count():
    vm = RemindersModel(reminder_list=sample_reminders())
    qt_adapter = ModelAdapter(vm)
    assert qt_adapter.columnCount() == len(C.ALL_COL_LABELS)
