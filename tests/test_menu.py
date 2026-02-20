"""Tests for the menu system."""
import pytest
from unittest.mock import MagicMock, patch
from rich.console import Console

from src.systems.menu import MenuSystem, MenuResult, TITLE_ART, SUBTITLE


def _make_menu() -> MenuSystem:
    """Return a MenuSystem backed by a non-interactive Console."""
    console = Console(file=MagicMock(), force_terminal=False)
    return MenuSystem(console)


# ---------------------------------------------------------------------------
# Attribute / structure tests (no I/O)
# ---------------------------------------------------------------------------

def test_menu_result_enum_values():
    """MenuResult has PLAY, RESUME, and QUIT variants."""
    assert hasattr(MenuResult, "PLAY")
    assert hasattr(MenuResult, "RESUME")
    assert hasattr(MenuResult, "QUIT")
    # All three must be distinct
    assert len({MenuResult.PLAY, MenuResult.RESUME, MenuResult.QUIT}) == 3


def test_title_art_is_non_empty():
    """TITLE_ART constant is a non-empty string."""
    assert isinstance(TITLE_ART, str)
    assert len(TITLE_ART.strip()) > 0


def test_subtitle_is_non_empty():
    """SUBTITLE constant is a non-empty string."""
    assert isinstance(SUBTITLE, str)
    assert len(SUBTITLE.strip()) > 0


def test_menu_system_instantiates():
    """MenuSystem can be constructed with a Console."""
    menu = _make_menu()
    assert isinstance(menu, MenuSystem)


# ---------------------------------------------------------------------------
# Behaviour tests (mock terminal I/O)
# ---------------------------------------------------------------------------

def test_show_main_menu_enter_returns_play():
    """Pressing ENTER on the main menu returns MenuResult.PLAY."""
    menu = _make_menu()

    with patch.object(menu, "_start_raw"), \
         patch.object(menu, "_stop_raw"), \
         patch.object(menu, "_render_main_menu"), \
         patch.object(menu, "_read_key", side_effect=['\r']):
        result = menu.show_main_menu()

    assert result == MenuResult.PLAY


def test_show_main_menu_space_returns_play():
    """Pressing SPACE on the main menu returns MenuResult.PLAY."""
    menu = _make_menu()

    with patch.object(menu, "_start_raw"), \
         patch.object(menu, "_stop_raw"), \
         patch.object(menu, "_render_main_menu"), \
         patch.object(menu, "_read_key", side_effect=[' ']):
        result = menu.show_main_menu()

    assert result == MenuResult.PLAY


def test_show_main_menu_q_returns_quit():
    """Pressing Q on the main menu returns MenuResult.QUIT."""
    menu = _make_menu()

    with patch.object(menu, "_start_raw"), \
         patch.object(menu, "_stop_raw"), \
         patch.object(menu, "_render_main_menu"), \
         patch.object(menu, "_read_key", side_effect=['q']):
        result = menu.show_main_menu()

    assert result == MenuResult.QUIT


def test_show_main_menu_escape_returns_quit():
    """Pressing ESC on the main menu returns MenuResult.QUIT."""
    menu = _make_menu()

    with patch.object(menu, "_start_raw"), \
         patch.object(menu, "_stop_raw"), \
         patch.object(menu, "_render_main_menu"), \
         patch.object(menu, "_read_key", side_effect=['escape']):
        result = menu.show_main_menu()

    assert result == MenuResult.QUIT


def test_show_main_menu_ignores_unknown_keys_then_plays():
    """Unknown keys are ignored; the next ENTER starts the game."""
    menu = _make_menu()

    with patch.object(menu, "_start_raw"), \
         patch.object(menu, "_stop_raw"), \
         patch.object(menu, "_render_main_menu"), \
         patch.object(menu, "_read_key", side_effect=[None, 'x', None, '\n']):
        result = menu.show_main_menu()

    assert result == MenuResult.PLAY


def test_show_pause_menu_p_returns_resume():
    """Pressing P on the pause menu returns MenuResult.RESUME."""
    menu = _make_menu()

    with patch.object(menu, "_start_raw"), \
         patch.object(menu, "_stop_raw"), \
         patch.object(menu, "_render_pause_menu"), \
         patch.object(menu, "_read_key", side_effect=['p']):
        result = menu.show_pause_menu()

    assert result == MenuResult.RESUME


def test_show_pause_menu_r_returns_resume():
    """Pressing R on the pause menu returns MenuResult.RESUME."""
    menu = _make_menu()

    with patch.object(menu, "_start_raw"), \
         patch.object(menu, "_stop_raw"), \
         patch.object(menu, "_render_pause_menu"), \
         patch.object(menu, "_read_key", side_effect=['r']):
        result = menu.show_pause_menu()

    assert result == MenuResult.RESUME


def test_show_pause_menu_enter_returns_resume():
    """Pressing ENTER on the pause menu returns MenuResult.RESUME."""
    menu = _make_menu()

    with patch.object(menu, "_start_raw"), \
         patch.object(menu, "_stop_raw"), \
         patch.object(menu, "_render_pause_menu"), \
         patch.object(menu, "_read_key", side_effect=['\r']):
        result = menu.show_pause_menu()

    assert result == MenuResult.RESUME


def test_show_pause_menu_q_returns_quit():
    """Pressing Q on the pause menu returns MenuResult.QUIT."""
    menu = _make_menu()

    with patch.object(menu, "_start_raw"), \
         patch.object(menu, "_stop_raw"), \
         patch.object(menu, "_render_pause_menu"), \
         patch.object(menu, "_read_key", side_effect=['q']):
        result = menu.show_pause_menu()

    assert result == MenuResult.QUIT
