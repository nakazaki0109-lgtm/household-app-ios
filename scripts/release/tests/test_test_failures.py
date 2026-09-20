from scripts.release.test_failures import build_errors, failed_tests

XCTEST_OUTPUT = """Test Suite 'DomainTests' started at 2026-09-20 15:00:00.000.
Test Case '-[HouseholdAppTests.DomainTests testMoneyRejectsNegative]' passed (0.001 seconds).
Test Case '-[HouseholdAppTests.DomainTests testBudgetOver]' failed (0.002 seconds).
Test Case '-[HouseholdAppTests.ServiceTests testUpsert]' failed (0.010 seconds).
Test Case '-[HouseholdAppTests.DomainTests testBudgetOver]' failed (0.002 seconds).
"""

NEW_FORMAT_OUTPUT = "Test case 'ServiceTests.testUpsert()' failed on 'iPhone 16 - HouseholdApp (123)' (0.010 seconds)."


def test_failed_test_names_are_extracted_in_order_without_duplicates():
    assert failed_tests(XCTEST_OUTPUT) == [
        "-[HouseholdAppTests.DomainTests testBudgetOver]",
        "-[HouseholdAppTests.ServiceTests testUpsert]",
    ]


def test_new_output_format_is_recognised():
    assert failed_tests(NEW_FORMAT_OUTPUT) == ["ServiceTests.testUpsert()"]


def test_passing_output_has_no_failures():
    assert failed_tests("Test Case '-[A b]' passed (0.1 seconds).") == []


def test_build_errors_are_extracted():
    output = "/x/Foo.swift:3:5: error: cannot find 'x' in scope\nnoise\n/x/Foo.swift:3:5: error: cannot find 'x' in scope\n"
    assert build_errors(output) == ["/x/Foo.swift:3:5: error: cannot find 'x' in scope"]
