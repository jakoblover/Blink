import praw
import yaml
import regex
import requests
import random



class RedditDownloader:
    def __init__(self):
        self._id = ''
        self._secret = ''
        self._useragent = ''
        self._user = ''
        self._password = ''
        self._download_limit = 100
        self._subreddits = []
        self._dict_metadata = {}

        self.load_config()

        self._reddit = praw.Reddit(client_id=self._id,
                             client_secret=self._secret,
                             user_agent=self._useragent,
                             username=self._user   ,
                             password=self._password)

        self.download()
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

                self._download_limit = configs['downloaders']['reddit']['params']['download_limit']
                self._download_batch_size = configs['downloaders']['reddit']['params']['download_batch_size']

        except EnvironmentError as e:
            print("Error when opening config. ",e)
            self._error_log("Error when opening config", e)
        except KeyError as e:
            print("Error when applying config. ",e)
            self._error_log("Error when applying configs", e)

    def _error_log(self, message, error):
        with open("logs/reddit-errors.log","a+") as f:
            f.write('{0}\n'.format(message))

    def _update_metadata_list(self,sub):
        subreddit = self._reddit.subreddit(sub)
        self._dict_metadata[sub] = subreddit.hot(limit=self._download_batch_size)

    def _decide_subreddit(self):
        return self._subreddits[random.randint(0, len(self._subreddits)-1)]

    def download(self):
        '''
        Decide what subreddit to download images from
        Download image if it hasn't been shown before or downloaded to folder buffer

        '''
        #Decide what subreddit to download from
        sub_to_download_from = self._decide_subreddit()

        #Has the metadata dictionary been updated recently? If not, update
        #if time_since_last_refresh >= download_interval:
        self._update_metadata_list(sub_to_download_from)

        #Download image if:
        #   1. Hasn't been shown before
        #   2. Is not in buffer folder (hasn't been downloaded recently)

        # Put in buffer




    # def fetch_image(self,url,post_id):
    #     '''
    #     Checks if the provided URL is direct image link
    #     Checks if we have downloaded it before
    #     Downloads imurl.split('.')[-1]  'age to slideshow folder
    #     '''
    #     #if(url matches regex and is not been downloaded before):
    #         #save image to folder
    #     if 'gif' in url.split('.')[-1]:
    #         img_data = requests.get(url).content
    #         with open('images/{0}'.format(post_id), 'wb') as handler:
    #             handler.write(img_data)
