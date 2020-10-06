import datetime

class CurrentTime():
    def get_current_epoch_seconds(self):
        return int(datetime.datetime.now().timestamp())

class MockCurrentTime(CurrentTime):
    def __init__(self, mock_epoch_seconds):
        self.mock_epoch_seconds = mock_epoch_seconds

    def get_current_epoch_seconds(self):
        return self.mock_epoch_seconds

    def set_current_epoch_seconds(self, mock_epoch_seconds):
        self.mock_epoch_seconds = mock_epoch_seconds
