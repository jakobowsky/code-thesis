import json
import enum

class FileType(enum.Enum):
    RESULTS = "results"
    RAW_DATA = "raw_data"

class FileClient:
    def __init__(self, results_path: str, raw_data_path: str):
        self.results_path = results_path
        self.raw_data_path = raw_data_path

    def read(self, file_type: FileType, filename: str):
        base_path = self.results_path if file_type == FileType.RESULTS else self.raw_data_path
        base_path = base_path.rstrip('/')
        with open(f"{base_path}/{filename}", 'r') as f:
            return json.load(f)

    def write(self, data, file_type: FileType, filename: str):
        base_path = self.results_path if file_type == FileType.RESULTS else self.raw_data_path
        base_path = base_path.rstrip('/')
        with open(f"{base_path}/{filename}", 'w') as f:
            json.dump(data, f, indent=2)
    