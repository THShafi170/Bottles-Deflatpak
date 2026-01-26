from bottles.backend.logger import Logger

logging = Logger()


class GSettingsStub:
    @staticmethod
    def get_boolean(key: str) -> bool:
        logging.warning(f"Stub GSettings key {key}=False")
        return False

    @staticmethod
    def get_string(key: str) -> str:
        logging.warning(f"Stub GSettings key {key}='default'")
        return "default"

    @staticmethod
    def get_int(key: str) -> int:
        logging.warning(f"Stub GSettings key {key}=0")
        return 0

    @staticmethod
    def set_string(key: str, value: str) -> None:
        logging.warning(f"Stub GSettings set {key}='{value}'")

    @staticmethod
    def set_boolean(key: str, value: bool) -> None:
        logging.warning(f"Stub GSettings set {key}={value}")

    @staticmethod
    def set_int(key: str, value: int) -> None:
        logging.warning(f"Stub GSettings set {key}={value}")
