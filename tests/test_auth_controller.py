import controllers.auth_controller as auth

def test_attempt_login(temp_data_dir):
    result = auth.attempt_login("admin", "password")
    assert result in (True, False, None)

def test_recover_password(temp_data_dir):
    auth.recover_password("user@example.com")
