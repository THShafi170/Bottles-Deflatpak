from bottles.backend.logger import Logger
from bottles.backend.utils.proc import ProcUtils
from bottles.backend.wine.wineprogram import WineProgram
from bottles.backend.wine.wineserver import WineServer


logging = Logger()


class WineBoot(WineProgram):
    program = "Wine Runtime tool"
    command = "wineboot"

    def send_status(self, status: int):
        if status == -2:
            return self.nv_stop_all_processes()

        states = {-1: "force", 0: "-k", 1: "-r", 2: "-s", 3: "-u", 4: "-i"}
        envs = {
            "WINEDEBUG": "-all",
            "DISPLAY": ":3.0",
            "WINEDLLOVERRIDES": "winemenubuilder=d",
        }

        if status == 0 and not WineServer(self.config).is_alive():
            logging.info("There is no running wineserver.")
            return

        if status in states:
            args = f"{states[status]} /nogui"
            self.launch(
                args=args,
                environment=envs,
                communicate=True,
                action_name=f"send_status({states[status]})",
            )
        else:
            raise ValueError(f"[{status}] is not a valid status for wineboot!")

    def force(self):
        return self.send_status(-1)

    def kill(self, force_if_stalled: bool = False):
        self.send_status(0)

        if force_if_stalled:
            wineserver = WineServer(self.config)
            if wineserver.is_alive():
                wineserver.force_kill()
                wineserver.wait()

    def restart(self):
        return self.send_status(1)

    def shutdown(self):
        return self.send_status(2)

    def update(self):
        return self.send_status(3)

    def init(self):
        return self.send_status(4)

    def nv_stop_all_processes(self):
        # First try to kill the wineserver and its children
        WineServer(self.config).force_kill()

        # Then manually look for any stragglers using the BOTTLE env var
        try:
            procs = ProcUtils.get_by_env(f"BOTTLE={self.config.Path}")
            for proc in procs:
                proc.kill(9)  # SIGKILL
                logging.info(f"Killed process with PID {proc.pid}.")
        except Exception as e:
            logging.error(f"Error stopping processes: {e}")
