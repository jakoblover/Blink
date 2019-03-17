import praw
import yaml
import regex
import requests
import random
import datetime
import utils
import os
from prawcore.exceptions import OAuthException

class RedditDownloader:
    def __init__(self):
        self._id = ''
        self._secret = ''
        self._useragent = ''
        self._user = ''
        self._password = ''
        self._download_batch_size = 0
        self._time_refresh_sub = 0
        self._media_filepath = ''
        self._last_image_found = None


        self._subreddits = []
        self._dict_metadata = {}
        self._supported_image_formats = [
            'png',
            'jpeg',
            'jpg',
            'gif'
        ]

        '''
        key: 'subreddit'
        value: (time_since_metadata_refresh,submissions_list)
        '''
        self.load_config()

        self._reddit = praw.Reddit(client_id=self._id,
                             client_secret=self._secret,
                             user_agent=self._useragent,
                             username=self._user,
                             password=self._password)

        for subreddit in self._subreddits:
            self._dict_metadata[subreddit] = (datetime.datetime.min,)

    def load_config(self):
        try:
            with open("config.yaml") as f:
                configs = yaml.safe_load(f)
                self._id = configs['downloaders']['reddit']['id']
                self._secret = configs['downloaders']['reddit']['secret']
                self._useragent = configs['downloaders']['reddit']['useragent']
                self._user = configs['downloaders']['reddit']['user']
                self._password = configs['downloaders']['reddit']['password']
                self._subreddits = configs['downloaders']['reddit']['subreddits']
                self._download_batch_size = configs['downloaders']['reddit']['params']['download_batch_size']
                self._time_refresh_sub = configs['downloaders']['reddit']['params']['time_refresh_sub']

                self._media_filepath = configs['params']['media_filepath']


        except EnvironmentError as e:
            print("Error when opening config. ",e)
            utils.error_log('RedditDownloader',"Error when opening config", e)
        except KeyError as e:
            print("Error when applying config. ",e)
            utils.error_log('RedditDownloader',"Error when applying configs", e)

    def _update_metadata_list(self,sub,type):
        subreddit = self._reddit.subreddit(sub)
        if type =='hot':
            self._dict_metadata[sub] = (datetime.datetime.now(), subreddit.hot(limit=self._download_batch_size))
        elif type == 'new':
            self._dict_metadata[sub] = (datetime.datetime.now(), subreddit.new(limit=self._download_batch_size))


    def _get_top_comment(self,submission):
        submission.comment_sort = 'best'
        submission.comment_limit = 1
        for top_level_comment in submission.comments:
            if isinstance(top_level_comment, praw.reddit.models.MoreComments):
                continue
            return top_level_comment.body
        return None

    def _find_new_image(self,log,sub):
        '''
        Compares the log of downloaded images, and compares it with the metadata dictionary.
        Return the first item that is not in the log.
        :return: Media object
        '''
        try:
            for submission in self._dict_metadata[sub][1]:
                file_format = submission.url.split('.')[-1]
                valid_url = file_format in self._supported_image_formats
                if not valid_url:
                    continue
                elif submission.id not in log:
                    file_name = '{0}.{1}'.format(submission.id, file_format)
                    self._last_image_found = utils.Media(id=submission.id,
                                                         filetype=file_format,
                                                         filepath=os.path.join(self._media_filepath,file_name),
                                                         title=submission.title,
                                                         url=submission.url,
                                                         top_comment=self._get_top_comment(submission),
                                                         source='/r/{0}'.format(sub)
                                                         )
                    print("Found image not in log ",self._last_image_found.id)
                    return self._last_image_found
            return None
        except OAuthException:
            print("Error in credentials for RedditDownloader")
            utils.error_log('RedditDownloader','Error in config. Check credentials.')
            return None

    def _save_image(self, media):
        '''
        Checks if the provided URL is direct image link
        Checks if we have downloaded it before

        Returns post_id if successfully wrote image to file
        Returns None if error occurred
        '''
        try:
            img_data = requests.get(media.url).content
            with open(os.path.join(self._media_filepath,'{0}.{1}'.format(media.id,media.filetype)), 'wb') as handler:
                handler.write(img_data)
                return media.id
        except:
            utils.error_log('RedditDownloader','Error when downloading image')
            return None




    def download(self, log):
        '''
        Decide what subreddit to download images from
        Download image if it hasn't been shown before or downloaded to folder buffer
        @TODO: Refresh a subreddit from hot if we haven't done so in a while to prevent only showing old "new" images
        @TODO: Prevent download from a stale subreddit for some hours (Long time since a new post)
        '''

        #Create a list of numbers from 0 to num_subreddits, and shuffle the order.
        idx_subs = [i for i in range(0,len(self._subreddits))]
        random.shuffle(idx_subs)

        #Try the first random subreddit. If no images are found, move to a new random sub.
        for i in range(0,len(self._subreddits)):
            sub_to_download_from = self._subreddits[idx_subs[i]]

            #Check if there are images to be downloaded
            time_since_refresh_seconds = (datetime.datetime.now() - self._dict_metadata[sub_to_download_from][0]).total_seconds()
            time_since_refresh_minutes = divmod(time_since_refresh_seconds, 60)[0]


            if time_since_refresh_minutes >= self._time_refresh_sub or self._find_new_image(log,sub_to_download_from) == None:
                print("Updating metadata list from ", sub_to_download_from)
                self._update_metadata_list(sub_to_download_from,'hot')
                if self._find_new_image(log,sub_to_download_from) == None:
                    self._update_metadata_list(sub_to_download_from,'new')
                    if self._find_new_image(log,sub_to_download_from) == None:
                        print("Could not find any images that have not been shown. Moving to another subreddit")
                        continue

            #Actually download the image to an image folder
            downloaded_id = self._save_image(self._last_image_found)
            if downloaded_id != None:
                return self._last_image_found

        return None


#Pick random sub
#Fetch metadata from hot
#Download images in hot if: not been shown before && not already downloaded && more recent than X hours (from config)
#If no images from the subreddit can be shown, pick another





