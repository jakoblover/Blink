import praw
import requests
import random
import datetime
import utils
import os
from downloaders import BaseDownloader

from prawcore.exceptions import OAuthException
from praw.exceptions import ClientException
import PIL.Image


class RedditDownloader(BaseDownloader):
    def __init__(self, config):
        self.config = config
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
        self._subreddits = []
        self._dict_metadata = {}
        self._supported_image_formats = ["png", "jpeg", "jpg", "gif"]
        self._downloader = "reddit"
        # self._downloaded_ids = utils.read_from_log(downloader=self._downloader)

        """
        key: 'subreddit'
        value: (time_since_metadata_refresh,submissions_list)
        """

        self._reddit = None

        for subreddit in self._subreddits:
            self._dict_metadata[subreddit] = (datetime.datetime.min,)

    def validate_config(self):
        pass

    def _update_metadata_list(self, sub, type):
        subreddit = self._reddit.subreddit(sub)
        if type == "hot":
            self._dict_metadata[sub] = (
                datetime.datetime.now(),
                subreddit.hot(limit=self._download_batch_size),
            )
        elif type == "new":
            self._dict_metadata[sub] = (
                datetime.datetime.now(),
                subreddit.new(limit=self._download_batch_size),
            )

    def _get_top_comment(self, submission):
        submission.comment_sort = "best"
        submission.comment_limit = 1
        for top_level_comment in submission.comments:
            if isinstance(top_level_comment, praw.reddit.models.MoreComments):
                continue
            return top_level_comment.body
        return None

    def _find_new_image(self, log, sub):
        """
        Compares the log of downloaded images, and compares it with the metadata dictionary.
        Return the first item that is not in the log.
        :return: Media object
        """
        try:
            for submission in self._dict_metadata[sub][1]:
                file_format = submission.url.split(".")[-1]
                valid_url = file_format in self._supported_image_formats
                if not valid_url:
                    continue
                elif submission.id not in log:
                    file_name = "{0}.{1}".format(submission.id, file_format)
                    file_path = os.path.join(self._media_filepath, file_name)
                    self._last_image_found = utils.Media(
                        id=submission.id,
                        filetype=file_format,
                        filepath=file_path,
                        title=submission.title,
                        url=submission.url,
                        top_comment=self._get_top_comment(submission),
                        source="/r/{0}".format(sub),
                    )

                    print("Found image not in log ", self._last_image_found.id)
                    return self._last_image_found
            return None
        except OAuthException as e:
            print("Error in credentials for RedditDownloader")
            utils.error_log("RedditDownloader", "Check config", e)
            return None
        except ClientException as e:
            print("Error in credentials for RedditDownloader")
            utils.error_log("RedditDownloader", "Check config", e)
            return None

    def _save_image(self, media):
        """
        Checks if the provided URL is direct image link
        Checks if we have downloaded it before

        Returns post_id if successfully wrote image to file
        Returns None if error occurred
        """
        try:
            img_data = requests.get(media.url).content
            with open(
                os.path.join(self._media_filepath, "{0}.{1}".format(media.id, media.filetype)),
                "wb",
            ) as handler:
                handler.write(img_data)
                return media
        except Exception as e:
            utils.error_log("RedditDownloader", "Error when downloading image", e)
            utils.log(
                downloader=self._downloader,
                list=self._downloaded_ids,
                id=media.id,
                max_log_size=self._max_log_size,
            )
            return None

    def download(self):
        """
        Decide what subreddit to download images from
        Download image if it hasn't been shown before or downloaded to folder buffer
        TODO: Refresh a subreddit from hot if we haven't done so in a while to prevent only showing old "new" images
        TODO: Prevent download from a stale subreddit for some hours (Long time since a new post)
        TODO: Some GIFs do not have the looping variable set, and won't loop
        TODO: Images should be downloaded to a temporary folder, and then be moved if it is valid. For now, if images are not valid media, it is stored in the same folder as valid media first and then deleted.
        """
        try:
            self._reddit = praw.Reddit(
                client_id=self._id,
                client_secret=self._secret,
                user_agent=self._useragent,
                username=self._user,
                password=self._password,
            )
        except Exception as e:
            utils.error_log("RedditDownloader", "Error creating reddit praw object", e)
            return None

        # Create a list of numbers from 0 to num_subreddits, and shuffle the order.
        idx_subs = [i for i in range(0, len(self._subreddits))]
        random.shuffle(idx_subs)

        # Try the first random subreddit. If no images are found, move to a new random sub.
        for i in range(0, len(self._subreddits)):
            sub_to_download_from = self._subreddits[idx_subs[i]]

            # Check if there are images to be downloaded
            time_since_refresh_seconds = (
                datetime.datetime.now() - self._dict_metadata[sub_to_download_from][0]
            ).total_seconds()
            time_since_refresh_minutes = divmod(time_since_refresh_seconds, 60)[0]

            if (
                time_since_refresh_minutes >= self._time_refresh_sub
                or self._find_new_image(self._downloaded_ids, sub_to_download_from) == None
            ):
                print("Updating metadata list from ", sub_to_download_from)
                self._update_metadata_list(sub_to_download_from, "hot")
                if self._find_new_image(self._downloaded_ids, sub_to_download_from) == None:
                    self._update_metadata_list(sub_to_download_from, "new")
                    if (
                        self._find_new_image(self._downloaded_ids, sub_to_download_from)
                        == None
                    ):
                        print(
                            "Could not find any images that have not been shown. Moving to another subreddit"
                        )
                        continue

            # Actually download the image to an image folder
            downloaded_media = self._save_image(self._last_image_found)
            print(downloaded_media)
            # Add parameters we don't know until image is downloaded
            if type(downloaded_media) is utils.Media:
                try:
                    (
                        downloaded_media.width,
                        downloaded_media.height,
                    ) = utils.get_width_height(downloaded_media.filepath)
                    if downloaded_media.filetype == "gif":
                        downloaded_media.duration = utils.get_gif_duration(
                            downloaded_media.filepath
                        )

                        print("GIF duration: ", downloaded_media.duration)
                except:
                    utils.error_log("RedditDownloader", "Error fetching image metadata")
                    utils.remove_media(downloaded_media.filepath)
                    return None
            else:
                return None

            if downloaded_media.filetype == "gif" and type(downloaded_media.duration) is None:
                utils.error_log("RedditDownloader", "GIF duration was 0")
                return None
            elif type(downloaded_media.width) is None or type(downloaded_media.height) is None:
                utils.error_log("RedditDownloader", "Width and height of image was undefined")
                return None

            if type(downloaded_media) == utils.Media:
                utils.log(
                    downloader=self._downloader,
                    list=self._downloaded_ids,
                    id=downloaded_media.id,
                    max_log_size=self._max_log_size,
                )
                return downloaded_media
            else:
                return None


# Pick random sub
# Fetch metadata from hot
# Download images in hot if: not been shown before && not already downloaded && more recent than X hours (from config)
# If no images from the subreddit can be shown, pick another
