from bottles.backend.utils.terminal import TerminalUtils


def test_execute_finds_supported_terminal(mocker):
    terminal = TerminalUtils()
    terminal.terminal = ["foot", "sh -c %s"]
    mocker.patch.object(terminal, "check_support", return_value=True)
    popen = mocker.patch("bottles.backend.utils.terminal.subprocess.Popen")
    popen.return_value.communicate.return_value = (b"", None)

    result = terminal.execute("wine game.exe")

    assert result is True
    assert popen.called


def test_execute_returns_false_when_no_terminal(mocker):
    terminal = TerminalUtils()
    mocker.patch.object(terminal, "check_support", return_value=False)

    result = terminal.execute("wine game.exe")

    assert result is False


def test_execute_passes_env_to_subprocess(mocker):
    terminal = TerminalUtils()
    terminal.terminal = ["foot", "sh -c %s"]
    mocker.patch.object(terminal, "check_support", return_value=True)
    popen = mocker.patch("bottles.backend.utils.terminal.subprocess.Popen")
    popen.return_value.communicate.return_value = (b"", None)
    env = {"MY_VAR": "hello"}

    terminal.execute("wine game.exe", env=env)

    call_env = popen.call_args.kwargs.get("env") or popen.call_args[1].get("env")
    assert call_env is not None
    assert call_env["MY_VAR"] == "hello"


def test_check_support_returns_false_when_no_terminals_available(monkeypatch):
    import shutil as _shutil

    monkeypatch.setattr(_shutil, "which", lambda _: None)
    terminal = TerminalUtils()
    assert terminal.check_support() is False


def test_supported_terminals_contain_modern_terminals():
    bins = [t[0] for t in TerminalUtils.terminals]
    assert "ptyxis" in bins
    assert "ghostty" in bins
    assert "alacritty" in bins
    assert "foot" in bins
    assert "konsole" in bins
    assert "kitty" in bins


def test_kde_desktop_prioritizes_konsole(monkeypatch):
    import shutil as _shutil

    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "KDE")
    monkeypatch.setenv("DESKTOP_SESSION", "plasma")
    monkeypatch.delenv("TERMINAL", raising=False)
    # Simulate both konsole and kitty being installed
    monkeypatch.setattr(
        _shutil,
        "which",
        lambda cmd: f"/usr/bin/{cmd}" if cmd in ["konsole", "kitty"] else None,
    )
    terminal = TerminalUtils()
    assert terminal.check_support() is True
    assert terminal.terminal[0] == "konsole"


def test_execute_formats_command_with_spaces(mocker):
    terminal = TerminalUtils()
    terminal.terminal = ["konsole", "--noclose -e sh -c %s"]
    mocker.patch.object(terminal, "check_support", return_value=True)
    popen = mocker.patch("bottles.backend.utils.terminal.subprocess.Popen")
    popen.return_value.communicate.return_value = (b"", None)

    cmd = "/usr/bin/gamemoderun '/home/user/Custom Runner/files/bin/wine' start /wait game.exe"
    result = terminal.execute(cmd)

    assert result is True
    call_args = popen.call_args[0][0]
    assert call_args == ["konsole", "--noclose", "-e", "sh", "-c", cmd]
    assert popen.call_args.kwargs.get("shell") is False


def test_xdg_terminal_exec_prioritized(monkeypatch):
    import shutil as _shutil

    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "KDE")
    monkeypatch.setenv("DESKTOP_SESSION", "plasma")
    monkeypatch.delenv("TERMINAL", raising=False)
    monkeypatch.setattr(
        _shutil,
        "which",
        lambda cmd: (
            f"/usr/bin/{cmd}"
            if cmd in ["xdg-terminal-exec", "konsole", "kitty"]
            else None
        ),
    )
    terminal = TerminalUtils()
    assert terminal.check_support() is True
    assert terminal.terminal[0] == "xdg-terminal-exec"


def test_wm_session_prioritizes_terminal_env(monkeypatch):
    import shutil as _shutil

    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "Hyprland")
    monkeypatch.setenv("DESKTOP_SESSION", "hyprland")
    monkeypatch.setenv("TERMINAL", "foot")
    monkeypatch.setattr(
        _shutil,
        "which",
        lambda cmd: f"/usr/bin/{cmd}" if cmd in ["foot", "kitty", "konsole"] else None,
    )
    terminal = TerminalUtils()
    assert terminal.check_support() is True
    assert terminal.terminal[0] == "foot"


def test_build_argv_supports_various_templates():
    cmd = "wine '/games/My Game/game.exe'"
    assert TerminalUtils.build_argv(["foot", "%s"], cmd) == [
        "foot",
        "sh",
        "-c",
        cmd,
    ]
    assert TerminalUtils.build_argv(["alacritty", "-e %s"], cmd) == [
        "alacritty",
        "-e",
        "sh",
        "-c",
        cmd,
    ]
    assert TerminalUtils.build_argv(["konsole", "--noclose -e sh -c %s"], cmd) == [
        "konsole",
        "--noclose",
        "-e",
        "sh",
        "-c",
        cmd,
    ]
    assert TerminalUtils.build_argv(
        ["konsole", "--noclose", "-e", "sh", "-c"], cmd
    ) == ["konsole", "--noclose", "-e", "sh", "-c", cmd]
