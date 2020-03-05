from queue import Queue

import praw
import requests
import random
import datetime
import utils
import os
import collections
from downloaders import BaseDownloader

from prawcore.exceptions import OAuthException
from praw.exceptions import ClientException
import PIL.Image

from type.Image import Image
from type.Media import Media


class RedditDownloader:
    def __init__(self, config, media_path, log_path):
        self.config = config
        self.media_path = media_path
        self.log_path = log_path

        self.validate_config()
        self.init()

    def init(self):

        self._id = self.config["id"]
        self._secret = self.config["secret"]
        self._useragent = self.config["useragent"]
        self._user = self.config["user"]
        self._password = self.config["password"]
        self._download_batch_size = self.config["download_batch_size"]
        self._time_refresh_sub = self.config["time_refresh_sub"]
        self._update_interval = self.config["update_interval"]
        self._show_top_comment = self.config["show_top_comment"]
        self._max_log_size = self.config["max_log_size"]

        self._last_image_found = None
        self._log_shown_images = collections.deque(maxlen=self._max_log_size)

        """
        key: 'subreddit'
        value: (time_since_metadata_refresh,submissions_list)
        """

        self._reddit = None

    def validate_config(self):
        pass

    def _metadata_list(self, sub, type):
        subreddit = self._reddit.subreddit(sub)
        if type == "hot":
            return subreddit.hot(limit=self._download_batch_size)
        elif type == "new":
            return subreddit.new(limit=self._download_batch_size)

    # def _get_top_comment(self, submission):
    #     submission.comment_sort = "best"
    #     submission.comment_limit = 1
    #     for top_level_comment in submission.comments:
    #         if isinstance(top_level_comment, praw.reddit.models.MoreComments):
    #             continue
    #         return top_level_comment.body
    #     return None

    def _find_new_image(self, sub):
        """
        Compares the log of downloaded images, and compares it with the metadata dictionary.
        Return the first item that is not in the log.
        :return: Media object
        """
        try:
            for submission in self._metadata_list(sub, "hot"):
                if submission.domain != "i.redd.it":
                    continue

                file_format = submission.url.split(".")[-1]
                file_name = submission.id
                if submission.id not in self._log_shown_images:
                    self._last_image_found = Image(
                        id=file_name,
                        file_format=submission.url.split(".")[-1],
                        file_path=os.path.join(self.media_path, f"{file_name}.{file_format}"),
                        title=submission.title,
                        url=submission.url,
                        # top_comment=self._get_top_comment(submission),
                        source="/r/{0}".format(sub),
                    )
                    print("Found image not in log ", self._last_image_found.id)
                    break

        except OAuthException as e:
            print("Error in credentials for RedditDownloader")
            utils.error_log("RedditDownloader", "Check config", e)
            return
        except ClientException as e:
            print("Error in credentials for RedditDownloader")
            utils.error_log("RedditDownloader", "Check config", e)
            return

    def _save_image(self):
        """
        Checks if the provided URL is direct image link
        Checks if we have downloaded it before

        Returns post_id if successfully wrote image to file
        Returns None if error occurred
        """
        img_data = requests.get(self._last_image_found.url).content

        with open(self._last_image_found.file_path, "wb",) as handler:
            handler.write(img_data)
            (
                self._last_image_found.width,
                self._last_image_found.height,
            ) = utils.get_width_height(self._last_image_found.file_path)

    def download(self, subreddit):
        """
        Decide what subreddit to download images from
        Download image if it hasn't been shown before or downloaded to folder buffer
        TODO: Buffer the subreddit list to avoid refreshing the list of posts every time we download
        """
        print("[RedditDownloader] Downloading from Reddit")

        try:
            self._reddit = praw.Reddit(
                client_id=self._id,
                client_secret=self._secret,
                user_agent=self._useragent,
                username=self._user,
                password=self._password,
            )
        except ClientException as e:
            print("[RedditDownloader] Wrong credentials")
            return

        self._find_new_image(subreddit)
        # Actually download the image to an image folder
        self._save_image()

        if len(self._log_shown_images) >= self._log_shown_images.maxlen:
            self._log_shown_images.popleft()
        self._log_shown_images.append(self._last_image_found)
        return self._last_image_found


# Pick random sub
# Fetch metadata from hot
# Download images in hot if: not been shown before && not already downloaded && more recent than X hours (from config)
# If no images from the subreddit can be shown, pick another
