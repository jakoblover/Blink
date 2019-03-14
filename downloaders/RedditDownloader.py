import praw
import yaml
import regex
import requests
import random
import datetime
from utils import error_log, Media


class RedditDownloader:
    def __init__(self):
        self._id = ''
        self._secret = ''
        self._useragent = ''
        self._user = ''
        self._password = ''
        self._download_batch_size = 0
        self._sub_refresh_timer = 0
        self._last_image_found = None

        self._subreddits = []
        self._dict_metadata = {}
        '''
        key: 'subreddit'
        value: (time_since_metadata_refresh,submissions_list)
        '''
        self.load_config()

        self._reddit = praw.Reddit(client_id=self._id,
                             client_secret=self._secret,
                             user_agent=self._useragent,
                             username=self._user   ,
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
                self._sub_refresh_interval = configs['downloaders']['reddit']['params']['sub_refresh_interval']

        except EnvironmentError as e:
            print("Error when opening config. ",e)
            error_log('RedditDownloader',"Error when opening config", e)
        except KeyError as e:
            print("Error when applying config. ",e)
            error_log('RedditDownloader',"Error when applying configs", e)


    def _update_metadata_list(self,sub,type):
        subreddit = self._reddit.subreddit(sub)
        if type =='hot':
            self._dict_metadata[sub] = (datetime.datetime.now(), subreddit.hot(limit=self._download_batch_size))
        elif type == 'new':
            self._dict_metadata[sub] = (datetime.datetime.now(), subreddit.new(limit=self._download_batch_size))

    def _find_new_image(self,log,sub):
        '''
        Compares the log of downloaded images, and compares it with the metadata dictionary.
        Return the first item that is not in the log.
        :return: Media object
        '''
        for submission in self._dict_metadata[sub][1]:
            if submission.id not in log:
                self._last_image_found = Media(id=submission.id,title=submission.title,url=submission.url)
                return self._last_image_found
        self._last_image_found = None
        return None

    def _fetch_image(self, url, post_id):
        '''
        Checks if the provided URL is direct image link
        Checks if we have downloaded it before
        Downloads imurl.split('.')[-1]  'age to slideshow folder
        '''
        if 'jpg' == url.split('.')[-1]:
            img_data = requests.get(url).content
            with open('images/{0}'.format(post_id), 'wb') as handler:
                handler.write(img_data)

    def download(self, log):
        '''
        Decide what subreddit to download images from
        Download image if it hasn't been shown before or downloaded to folder buffer
        @TODO: Refresh a subreddit from hot if we haven't done so in a while to prevent only showing old "new" images
        @TODO: Prevent download from a stale subreddit for some hours (Long time since a new post)
        '''
        #Pick a random subreddit
        sub_to_download_from = self._subreddits[random.randint(0, len(self._subreddits)-1)]
        print("Downloading from ",sub_to_download_from)

        #Check if there are images to be downloaded

        time_since_refresh_seconds = (datetime.datetime.now() - self._dict_metadata[sub_to_download_from][0]).total_seconds()
        time_since_refresh_minutes = divmod(time_since_refresh_seconds, 60)[0]
        print("Last time updated: {0} minutes ago".format(time_since_refresh_minutes))


        if time_since_refresh_minutes >= self._sub_refresh_timer or self._find_new_image(log,sub_to_download_from) == None:
            print("Updating metadata list")
            self._update_metadata_list(sub_to_download_from,'hot')
            if self._find_new_image(log,sub_to_download_from) == None:
                self._update_metadata_list(sub_to_download_from,'new')
                if self._find_new_image(log,sub_to_download_from) == None:
                    print("Could not find any images that have not been shown")
                    return None

        #Actually download the image to an image folder
        self._fetch_image(self._last_image_found.url,self._last_image_found.id)
        return self._last_image_found


#Pick random sub
#Fetch metadata from hot
#Download images in hot if: not been shown before && not already downloaded && more recent than X hours (from config)
#If no images from the subreddit can be shown, pick another





