def test_placeholder_module_imports() -> None:
    from veyra.main import PlaceholderWindow, create_application

    assert PlaceholderWindow is not None
    assert callable(create_application)

