# Python

### Password Checker
```
Requires the requests module
```
Uses API call to check whether or not a given password has been hacked at some point, and how many times


### Twitter Bot
```
Requires numpy, scikit-learn, nltk, tweepy and dateutils.
```
Creates a twitter bot that actively replies to mentions using various corpora and picking responses that closely match the given text. Not very intellegent responses at this point, but I plan on improving it to use a convolutional neural network in the future.

You will need to create an XML file structured like this so that it can link to your twitter bot account. This should go in the executing directory (/venv in this case)
```
<twitterConfig>
  <consumerKey key='yourKey' secret='yourSecret' />
  <accessToken key='yourToken' secret'yourSecret' />
</twitterConfig>
```
