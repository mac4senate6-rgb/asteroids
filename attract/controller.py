class AttractController:
    def __init__(self, start_time: int) -> None:
        self.start_time = start_time
        self.display_interval = 16000

    def current_display(self, current_time: int) -> str:
        elapsed_time = current_time - self.start_time
        interval_number = elapsed_time // self.display_interval

        if interval_number % 2 == 0:
            return "DEMO"

        return "HIGH_SCORES"

    def reset(self, start_time: int) -> None:
        self.start_time = start_time
