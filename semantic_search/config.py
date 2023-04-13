import pathlib
from envyaml import EnvYAML


class Config:
    BASE_DIR = pathlib.Path(__file__).parent.parent
    CONFIG_FILE_PATH = BASE_DIR / 'config.yml'
    TITLES_FILE_PATH = BASE_DIR / 'feline_diseases.txt'

    def __init__(self):
        settings = EnvYAML(str(self.CONFIG_FILE_PATH), strict=False)
        self._settings = settings

    def __getitem__(self, item):
        return self._settings[item]


config = Config()
