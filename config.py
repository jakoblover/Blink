import yaml
import importlib


class Config:
    def __init__(self, path):
        self.config_dict = dict()

        self._load_config(path)
        self._validate_config()

    def _validate_config(self):
        """
        Checks if the config has the correct base configs set
        :return:
        """
        try:
            # Parameters #
            assert type(self.config_dict["parameters"]["media_duration"]) == int
            assert type(self.config_dict["parameters"]["min_video_duration"]) == int
            assert type(self.config_dict["parameters"]["max_video_duration"]) == int
            assert type(self.config_dict["parameters"]["video_iterations"]) == int
            assert type(self.config_dict["parameters"]["time_delay_text"]) == int
            assert type(self.config_dict["parameters"]["max_queue_size"]) == int
            assert type(self.config_dict["parameters"]["media_path"]) == str
            assert type(self.config_dict["parameters"]["log_path"]) == str
            assert type(self.config_dict["parameters"]["min_aspect_ratio"]) == float
            assert type(self.config_dict["parameters"]["max_aspect_ratio"]) == float
            assert type(self.config_dict["parameters"]["title_font_size"]) == int

            # Top level config values #
            assert type(self.config_dict["downloaders"]) == dict
            assert type(self.config_dict["weights"]) == dict
            assert type(self.config_dict["schedule"]) == dict

            # Check that all downloaders are configured correctly
            # Example:
            #
            # reddit:
            #   class: RedditDownloader
            #   conf:
            #       id:
            #       secret:
            for _downloader_name, _config in self.config_dict["downloaders"].items():

                assert type(_downloader_name) == str
                assert type(_config) == dict
                assert type(_config["class"]) == str
                assert type(_config["conf"]) == dict

                # Check if we are able to create a class
                _module = importlib.import_module("downloaders")
                _class = getattr(_module, _config["class"])
                instance = _class(self.get_downloader_config(_downloader_name))

        except AssertionError as e:
            print(f"Invalid config: {e.args[0]}")
            raise

        except KeyError as e:
            print(f'Error when accessing key "{e.args[0]}" in config')
            raise

    def _load_config(self, path):
        """
        Reads config from file
        :param path:
        :return:
        """
        try:
            with open(path) as f:
                configs = yaml.safe_load(f)
                self.config_dict = configs

        except FileNotFoundError:
            print("Config file does not exist")
            raise

    def get_scheduler_config(self):
        """
        Extracts the needed config parameters for the scheduler
        :return: dictionary with config
        """
        return_dict = dict()
        return_dict.update({"parameters": self.config_dict["parameters"]})
        return_dict.update({"weights": self.config_dict["weights"]})
        return_dict.update({"schedule": self.config_dict["schedule"]})

        return return_dict

    def get_downloader_config(self, downloader_name):
        return_dict = dict()
        return_dict.update({"parameters": self.config_dict["parameters"]})
        return_dict.update(self.config_dict["downloaders"][downloader_name]["conf"])

        return return_dict

    def get_gui_config(self):
        return self.config_dict["parameters"]

    def get_downloaders(self):
        """
        Extracts downloaders from config
        :return: dictionary with downloaders and their configs
        """
        return self.config_dict["downloaders"]

    def get_queue_size(self):
        return self.config_dict["parameters"]["max_queue_size"]

    def get_media_path(self):
        return self.config_dict["parameters"]["media_path"]

    def get_log_path(self):
        return self.config_dict["parameters"]["log_path"]
