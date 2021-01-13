# MailBot

MailBot is a way to add functions to a discord bot that scrapes USPS Informed Deliver and messages a user about their incoming mail, as well as allows them to fetch the tracking history of a given tracking number.

The Informed Deliver scraper can also be attached to a cron task or task scheduler which runs the oneshot.py script. This will still message a user about their incoming mail, but it is not tied to having a discord bot being up and running.

MailBot is mainly made for personal use so code is not guaranteed to work for every environment out of the box.

## What is implemented
- Log into informed delivery, scrape the letter mail data for that day
- Scraped data for incoming packages


## Dependencies

## TO DO
- figure out how to configure a cron task using bot commands
- add better retry and error checking logic
- implement scraping information given a tracking number(s) using the USPS api wrapper
- revamp README so that it looks good
