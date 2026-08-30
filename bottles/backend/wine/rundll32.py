from bottles.backend.logger import Logger
from bottles.backend.wine.wineprogram import WineProgram

logging = Logger()


class RunDLL32(WineProgram):
    program = "32-bit DLLs loader and runner"
    command = "rundll32"

    def run_dialog(self):
        return self.launch(args="shell32.dll,#61", action_name="run_dialog")
