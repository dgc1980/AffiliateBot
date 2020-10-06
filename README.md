# AffiliateBot

This bot is used for subreddits,

the function is as follows,

when a submission or a comment is posted, it will extract the urls, check them against a whitelist, if the url is not with the whitelist, it will attempt to load the contents of the url and parse it for different types of affiliate links and report the submission or comment if one is detected,

this is useful for subs that are popular with spamming to help your moderators do what they do best and ban the spammer.

please note, that if the bot reports a post, it is still best if you check the comment/affected url just to make sure.

if you need any help with the bot, or setting up hosting for it, you are welcome to contact me directly.


### updates:
#### 07/10/2020
```
Added scanning of url redirects to match affiliate matches before scanning content
Added option for scanning link anchors for mismatched links e.g. [https://amazon.com/dp/item](https://linktospamsite.com) see Config.py
```
