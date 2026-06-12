import pytest

from windows_input import hotkey_to_vks, key_name_to_vk


def test_function_key_mapping():
    assert key_name_to_vk("F6") == 0x75


def test_tk_modifier_name_mapping():
    assert key_name_to_vk("Shift_L") == 0xA0


def test_hotkey_combo_mapping():
    assert hotkey_to_vks("ctrl+shift+a") == [0x11, 0x10, 0x41]


def test_unsupported_key_name():
    with pytest.raises(ValueError):
        key_name_to_vk("not-a-real-key")
