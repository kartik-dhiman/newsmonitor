from django.core.management.base import BaseCommand, CommandError

from login.models import *

import feedparser
import datetime

from newspaper.article import Article, ArticleException

import logging
logger = logging.getLogger(__name__)

from tqdm import tqdm

from progressbar import ProgressBar
pbar = ProgressBar()

class Command(BaseCommand):
    help = 'Fetch stories of the Sources saved, all at once...!'

    def handle(self, *args, **options):
        source_obj = Sourcing.objects.all()
        for list_item in tqdm(source_obj):
                # Parse the RSS URL and get the data
                feed_data = feedparser.parse(list_item.rss_url)

                # Detects if the Url is not well formed RSS
                if feed_data.bozo == 1:
                    logger.debug("Not a RSS url :    %s" % list_item.rss_url)
                else:
                    for data in tqdm(feed_data.get('entries')):
                        story_url = data.get('link')

                        # If RSS is Empty return Story listing page
                        if story_url is None:
                            logger.debug("No feed data in RSS URL:   %s" % list_item.rss_url)
                        else:

                            # Use newspaper library to download the article
                            article = Article(story_url)
                            try:
                                article.download()
                            except ArticleException:
                                logger.debug("Article Download exception in : %s" % story_url)


                            # Try to Parse Article
                            try:
                                article.parse()
                            except ArticleException:
                                logger.debug("Article parse exception in : %s" % story_url)

                            article_instance = article

                            if article_instance.publish_date is None:
                                article_instance.publish_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            # Check if story exist
                            try:
                                check_story_url = Stories.objects.get(url=story_url)

                            except check_story_url.DoesNotExist:
                                story = Stories(
                                    title=article_instance.title,
                                    source=list_item,
                                    pub_date=article_instance.publish_date,
                                    body_text=article_instance.text,
                                    url=article_instance.url
                                )
                                story.save()

