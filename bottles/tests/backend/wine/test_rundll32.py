from unittest.mock import patch

from bottles.backend.models.config import BottleConfig
from bottles.backend.wine.rundll32 import RunDLL32


def test_rundll32_run_dialog():
    config = BottleConfig(Name="Test")
    program = RunDLL32(config)

    with patch.object(program, "launch") as mock_launch:
        program.run_dialog()
        mock_launch.assert_called_once_with(
            args="shell32.dll,#61",
            action_name="run_dialog",
        )
