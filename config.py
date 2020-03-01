import sys

import yaml
import importlib


class Config:
    def __init__(self, path):
        self.config_dict = dict()

        self._load_config(path)
        self._validate_config()

    def _validate_config(self):
        try:
            # Parameters #
            assert type(self.config_dict["parameters"]["image_duration"]) == int
            assert type(self.config_dict["parameters"]["min_gif_duration"]) == int
            assert type(self.config_dict["parameters"]["max_gif_duration"]) == int
            assert type(self.config_dict["parameters"]["gif_iterations"]) == int
            assert type(self.config_dict["parameters"]["time_delay_text"]) == int
            assert type(self.config_dict["parameters"]["max_queue_size"]) == int
            assert type(self.config_dict["parameters"]["media_filepath"]) == str
            assert type(self.config_dict["parameters"]["log_filepath"]) == str
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
                instance = _class(_config)

            # Check that the weighting section sums up to 1.0
            _weights = 0
            for k, v in self.config_dict["weights"].items():
                _weights += v
            assert _weights == 1

        except AssertionError as e:
            raise

        except KeyError as e:
            print(f'Error when accessing key "{e.args[0]}" in config')
            raise

    def _load_config(self, path):
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

    def get_downloaders(self):
        """
        Extracts downloaders from config
        :return: dictionary with downloaders and their configs
        """
        return self.config_dict["downloaders"]
