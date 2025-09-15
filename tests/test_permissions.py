from core.permissions import is_admin

def test_is_admin_returns_bool():
    assert isinstance(is_admin(), bool)
