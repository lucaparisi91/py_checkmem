import signal


class termination:

    def start_to_close(self, signum, frame):
        print("Terminating")
        self.terminating = True

    def __init__(self):

        self.terminating = False
        signal.signal(signal.SIGTERM, self.start_to_close)
        signal.signal(signal.SIGINT, self.start_to_close)
