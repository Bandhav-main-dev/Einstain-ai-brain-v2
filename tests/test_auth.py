from monitor.auth import (
    create_password_record,
    verify_password,
)


def test_password_record_verification():
    record = create_password_record("Einstein-Test-123")

    assert verify_password(
        "Einstein-Test-123",
        record["salt"],
        record["password_hash"],
    )


def test_wrong_password_fails():
    record = create_password_record("Einstein-Test-123")

    assert not verify_password(
        "wrong-password",
        record["salt"],
        record["password_hash"],
    )
