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
