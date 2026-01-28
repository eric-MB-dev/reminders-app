from app.wx_ui.view_model import RemindersViewModel
from tests.fixtures.reminder_factory import sample_reminders, sample_display_rows

def test_viewmodel_rows():
    reminders = sample_reminders()
    for r in reminders:
        print("WHEN TYPE:", type(r.when), r.when)
    vm = RemindersViewModel(reminder_list=reminders)   # No data manager for this test
    
    expected = sample_display_rows()
    actual = vm.get_display_rows()
    assert expected == actual
    
from tests.fixtures.mock_reminders import mock_reminders
def test_viewmodel_column_alignment():
    
    vm = RemindersViewModel(reminder_list=mock_reminders)

    # 1. Column labels define the contract
    expected_cols = len(vm.col_labels)

    # 2. ViewModel must report the same count
    assert vm.get_col_count() == expected_cols

    # 3. Every display row must match the column count
    for row in vm.get_display_rows():
        assert len(row) == expected_cols
