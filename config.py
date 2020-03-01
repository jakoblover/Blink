import yaml


class Config:
    def __init__(self, path):
        try:
            with open("config.yaml") as f:
                configs = yaml.safe_load(f)
                self._max_queue_size = configs["params"]["max_queue_size"]
                self._image_duration = configs["params"]["image_duration"]
                self._time_delay_text = configs["params"]["time_delay_text"]
                self._media_filepath = configs["params"]["media_filepath"]
                self._log_filepath = configs["params"]["log_filepath"]
                self._title_font_size = configs["params"]["title_font_size"]
                self._min_gif_duration = configs["params"]["min_gif_duration"]
                self._max_gif_duration = configs["params"]["max_gif_duration"]
                self._gif_iterations = configs["params"]["gif_iterations"]
        except FileNotFoundError:
            print("Config file does not exist")
        except EnvironmentError:
            print("Error when opening config. ", e)
        except KeyError as e:
            print("Could not find ", e)


# all parameters exist
# downloaders entry exists and is list that contains
#     - class
#     - conf
# and checks that "class".py exists
# weights has correct entries and sum to 1.0
# schedule exists and is list with correct entries
