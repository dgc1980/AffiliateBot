import time
import praw
import prawcore
import requests
import logging
import re
import os
import datetime
import gc


import Config

reddit = praw.Reddit(client_id=Config.cid,
                     client_secret=Config.secret,
                     password=Config.password,
                     user_agent=Config.agent,
                     username=Config.user)
subreddit = reddit.subreddit(Config.subreddit)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=Config.apppath+'report.log',
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
os.environ['TZ'] = 'America/Los_Angeles'

f = open(Config.apppath+"submissionids.txt","a+")
f.close()
f = open(Config.apppath+"commentids.txt","a+")
f.close()


def checkanchors( comment ):
  anchors = re.findall('\[(\S+)\]\((\S+)\)', comment)
  for anchor in anchors:
    if Config.AnchorMatch == 'DomainOnly':
      if any(s in anchor[0] for s in ['.co','.com','.net', '.io', '.org', '.gg']):
        if getdomain( anchor[0] ):
          if getdomain(anchor[0]) != getdomain(anchor[1]):
            return True


def submissionID(postid):
    f = open(Config.apppath+"submissionids.txt","a+")
    f.write(postid + "\n")
    f.close()

def commentID(postid):
    f = open(Config.apppath+"commentids.txt","a+")
    f.write(postid + "\n")
    f.close()

def getdomain( url ):
    match1 = re.search("(?:https?:\/\/)?(?:www\.)?([\w\-\.]+)", url)
    if match1:
      return match1.group(1)
    return None

def check_url( url ):
    if re.search("(?:https?:\/\/)?(?:www\.)?([\w\-\.]+)\/", url) is not None:
        forceload = False
        for greylist in Config.Greylist:
            if greylist in url.lower():
                forceload = True
        if getdomain(url) not in Config.Whitelist or forceload:
            logging.info("checking url " + url)
            try:
                r = requests.get(url)
                if r.history:
                    for reqs in r.history:
                        print("redirects  " + reqs.url)
                        for affdata in Config.AffiliateData:
                            if re.search(affdata, reqs.url.lower() ) is not None:
                                return( "Found Generic Affiliate Information In Redirect" )
                    print("redirects  " + r.url)
                    for affdata in Config.AffiliateData:
                        if re.search(affdata, r.url.lower() ) is not None:
                            return( "Found Generic Affiliate Information In Redirect" )


                if re.search("amzn.to|amazon\.co.*tag=|amazon\.com\/.*asin", r.text.lower()) is not None:
                    return( "Amazon Affailiates Found" )
                if re.search("(amzn_assoc_tracking_id|amazon-adsystem.com)", r.text.lower()) is not None:
                    return( "Amazon Ads found, may be spam" )
                if re.search("shopify.com|wix.com", r.text.lower()) is not None:
                    return( "Wix/Shopify Found check if legit store" )
                for affdata in Config.AffiliateData:
                    if re.search(affdata, r.text ) is not None:
                        return( "Found Generic Affiliate Information" )
                return
            except:
                logging.info("error checking " + url)



def check_comment(comment):
    commentID(comment.id)
    urls = re.findall('(?:(?:https?):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', comment.body)
    if len(urls) == 0:
        logging.info("NO LINK FOUND skipping: " + comment.id)
        return
    # remove duplicate URLs
    unique_urls = []
    for url in urls:
        if url in unique_urls:
            continue
        else:
            unique_urls.append(url)

    if Config.CheckAnchors:
        if checkanchors( comment.body ):
            comment.report( "Affiliate Bot: " + "Found Mismatched Anchor/Link" )
            return

    for url in unique_urls:
        urlcheck = check_url( url )
        if urlcheck:
            comment.report( "Affiliate Bot: " + urlcheck )
            return


def check_post(submission):
    submissionID(submission.id)
    if submission.is_self:
        urls = re.findall('(?:(?:https?):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', submission.selftext)
        if len(urls) == 0:
            logging.info("NO LINK FOUND skipping: " + submission.title)
            return
    # remove duplicate URLs
        unique_urls = []
        for url in urls:
          if url in unique_urls:
            continue
          else:
            unique_urls.append(url)
        for url in unique_urls:
            urlcheck = check_url( url )
            if urlcheck:
                submission.report( "Affiliate Bot: " + urlcheck )
                return

    if not submission.is_self:
        url = submission.url
        urlcheck = check_url( url )
        if urlcheck:
            submission.report( urlcheck )
            return





posts = subreddit.stream.submissions(pause_after=-1)
cmts = subreddit.stream.comments(pause_after=-1)

while True:
    for post in posts:
        if post is None:
            break
        print( "checking post")
        check_post(post)
    for cmt in cmts:
        if cmt is None:
            break
        print( "checking comment")
        check_comment(cmt)

