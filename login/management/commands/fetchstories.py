from django.core.management.base import BaseCommand, CommandError

from login.models import *

import pytz
import feedparser
import datetime
from datetime import timezone

from newspaper.article import Article

import logging

from progressbar import ProgressBar
pbar = ProgressBar()

class Command(BaseCommand):
    help = 'Fetch stories of the Sources saved, all at once...!'

    def handle(self, *args, **options):
        source_obj = Sourcing.objects.all()
        for list_item in pbar(source_obj):
                # Parse the RSS URL and get the data
                feed_data = feedparser.parse(list_item.rss_url)

                # Detects if the Url is not well formed RSS
                if feed_data.bozo == 1:
                    logging.info("Not a proper url :    %s" % list_item.rss_url)
                else:
                    for data in feed_data.get('entries'):
                        story_url = data.get('link')

                        # If RSS is Empty return Story listing page
                        if story_url is None:
                            logging.info("Story URl broken for %s" % data)
                        else:
                            # Use newspaper library to download the article
                            article = Article(story_url)
                            article.download()

                            # Try to Parse Article
                            try:
                                article.parse()
                            except Exception:
                                logging.info("Exception while downloading article %s", article)

                            article_instance = article

                            if article_instance.publish_date is None:
                                article_instance.publish_date = datetime.datetime.now()

                            try:
                                # Check if story exist
                                Stories.objects.get(url=story_url)
                            except Stories.DoesNotExist:
                                story = Stories(
                                    title=article_instance.title,
                                    source=list_item,
                                    pub_date=article_instance.publish_date,
                                    body_text=article_instance.text,
                                    url=article_instance.url
                                )
                                story.save()

