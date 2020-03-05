import os
import PIL.Image
from type.Media import Media
from validators.ImageValidator import ImageValidator
from validators.VideoValidator import VideoValidator


def error_log(sender="etc", message="An error has occured", error=""):

    with open("logs/{0}-errors.log".format(sender), "a+") as f:
        f.write("[ERROR] {0}. {1}\n".format(message, error))


def remove_all_media(file_path):
    for file in os.listdir(file_path):
        file_path = os.path.join(file_path, file)

        if os.path.isfile(file_path):
            os.unlink(file_path)


def prepare_folders(media_path, log_path):
    try:
        os.makedirs(media_path)
        os.makedirs(log_path)
    except FileExistsError:
        pass


def get_width_height(filepath):
    img = PIL.Image.open(filepath)
    width, height = img.size[0], img.size[1]
    return width, height


def get_gif_duration(filepath):
    img = PIL.Image.open(filepath)
    img.seek(0)
    frames = duration = 0
    try:
        img = PIL.Image.open(filepath)
        img.seek(0)
        frames = duration = 0
        try:
            while True:
                frames += 1
                duration += img.info["duration"]
                img.seek(img.tell() + 1)
        except EOFError:
            return frames / duration * 1000
    except Exception as e:
        error_log("utils", "Error fetching gif duration", e)
        return None


# def get_width_height(filepath):
#     try:
#         img = PIL.Image.open(filepath)
#         width, height = img.size[0], img.size[1]
#         return width, height
#     except Exception as e:
#         print("Big fugg when fetching height and width")
#         error_log(
#             "utils",
#             "Width and height could not be extracted. Image was probably not an image file.",
#             e,
#         )
#         return None, None


def is_valid_media(media):
    return True
    if type(media) != Media:
        return False

    validator = None
    if media.file_format in ["png", "jpg", "jpeg", "bmp"]:
        validator = ImageValidator(media)
    elif media.file_format in ["mkv", "mp4"]:
        validator = VideoValidator(media)
    else:
        return False

    return validator.validate()


def read_from_log(downloader=""):
    try:
        with open("logs/downloaded-images-{0}.log".format(downloader), "r") as f:
            return f.read().split("\n")
    except EnvironmentError as e:
        error_log("DownloaderThread", "Error reading log file", e)
        return []


def write_to_log(downloader, list):
    try:
        with open("logs/downloaded-images-{0}.log".format(downloader), "w+") as f:
            f.truncate()
            f.write("\n".join(list))
    except EnvironmentError as e:
        error_log("DownloaderThread", "Error writing to log file", e)


def log(downloader="", list=None, id=None, max_log_size=1000):
    while len(list) >= max_log_size:
        list.pop(0)
    list.append(id)
    write_to_log(downloader, list)
