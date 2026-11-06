import os
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


class ButtonTests(unittest.TestCase):
    def setUp(self):
        main._OBJECTS.clear()
        main._GAME_STATE = "HOLD"
        main._BEAN_OR_NO_BEAN = False

    def test_button_invokes_callback_only_once_while_mouse_is_held(self):
        callback = Mock()
        button = main.Button(10, 20, 100, 40, "Ready!", callback)

        with patch.object(main.p.mouse, "get_pos", return_value=(20, 30)), patch.object(
            main.p.mouse, "get_pressed", return_value=(True, False, False)
        ):
            button.process()
            button.process()

        callback.assert_called_once_with()
        self.assertTrue(button.pressed)

    def test_button_uses_hover_color_for_its_outline_and_label(self):
        button = main.Button(10, 20, 100, 40, "Ready!", lambda: None)
        calls = []
        text_surface = Mock()
        text_surface.get_rect.return_value.width = 20
        text_surface.height = 20
        font = Mock()
        font.render.return_value = text_surface

        with patch.object(main.p.mouse, "get_pos", return_value=(20, 30)), patch.object(
            main.p.mouse, "get_pressed", return_value=(False, False, False)
        ), patch.object(main.p.draw, "rect", side_effect=lambda *args: calls.append(args)), patch.object(
            main, "screen"
        ) as screen, patch.object(main, "font", font):
            button.process()

        self.assertEqual(calls[0][1], (255, 255, 255))
        self.assertEqual(calls[1][1], button.fillColors["hover"])
        font.render.assert_called_once_with("Ready!", True, button.fillColors["hover"])
        screen.blit.assert_called_once_with(text_surface, [50.0, 30.0])


class GameActionTests(unittest.TestCase):
    def setUp(self):
        main._OBJECTS.clear()
        main._BEAN_OR_NO_BEAN = False
        main._BEAN_ACCEPTED = False
        main._WIZARD_SUMMONED = False

    def test_deal_accepts_bean_and_spawns_celebration(self):
        main.spawn_decision_buttons()
        self.assertEqual(len([b for b in main._OBJECTS if isinstance(b, main.Button)]), 2)

        with patch.object(main, "spawn_firework") as spawn_firework, patch.object(
            main, "play_sound_effect"
        ) as play_sound, patch.object(main, "Bean") as bean:
            main.deal()

        self.assertFalse(main._BEAN_OR_NO_BEAN)
        self.assertTrue(main._BEAN_ACCEPTED)
        self.assertEqual(spawn_firework.call_count, 3)
        play_sound.assert_called_once_with("assets/deal.mp3")
        bean.assert_called_once_with("bean")
        self.assertEqual(len([b for b in main._OBJECTS if isinstance(b, main.Button)]), 0)

    def test_no_deal_plays_sound_and_displays_no_bean(self):
        main.spawn_decision_buttons()
        self.assertEqual(len([b for b in main._OBJECTS if isinstance(b, main.Button)]), 2)

        with patch.object(main, "play_sound_effect") as play_sound, patch.object(main, "Bean") as bean:
            main.no_deal()

        self.assertFalse(main._BEAN_OR_NO_BEAN)
        play_sound.assert_called_once_with("assets/deal.mp3")
        bean.assert_called_once_with("no_bean")
        self.assertEqual(len([b for b in main._OBJECTS if isinstance(b, main.Button)]), 0)

    def test_wizard_rings_spawns_decision_buttons(self):
        main._WIZARD_SUMMONED = True
        with patch.object(main.m.music, "get_busy", return_value=False), patch.object(
            main, "play_sound_effect"
        ):
            main.wizard_rings()

        self.assertTrue(main._BEAN_OR_NO_BEAN)
        buttons = [b for b in main._OBJECTS if isinstance(b, main.Button)]
        self.assertEqual(len(buttons), 2)
        self.assertFalse(buttons[0].pressed)
        self.assertFalse(buttons[1].pressed)

    def test_selecting_largest_bean_uses_big_beans_sound(self):
        with patch.object(main.p.image, "load", return_value=main.p.Surface((100, 40))):
            slider = main.AmountSlider(0, 0, 100, 40, "500", "red", 10)

        with patch.object(main.p.mouse, "get_pos", return_value=(10, 10)), patch.object(
            main.p.mouse, "get_pressed", return_value=(True, False, False)
        ), patch.object(main, "play_sound_effect") as play_sound:
            slider.process()

        play_sound.assert_called_once_with("assets/big_beans_gone.mp3")
        self.assertTrue(slider.pressed)
        self.assertEqual(slider.state, "bye bye")

    def test_selecting_a_smaller_bean_uses_regular_selection_sound(self):
        with patch.object(main.p.image, "load", return_value=main.p.Surface((100, 40))):
            slider = main.AmountSlider(0, 0, 100, 40, "200", "red", 9)

        with patch.object(main.p.mouse, "get_pos", return_value=(10, 10)), patch.object(
            main.p.mouse, "get_pressed", return_value=(True, False, False)
        ), patch.object(main, "play_sound_effect") as play_sound:
            slider.process()

        play_sound.assert_called_once_with("assets/box_open.mp3")


if __name__ == "__main__":
    unittest.main()
