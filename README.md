# NeuraLingo-Tutorial-TwitterBot-HateSpeech
This repository contains a tutorial to build a Twitter Bot that classifies hate and offensive tweets using NeuralSpace's NeuraLingo (NLU) API.  

Let us get started!

## Install requirements

To make the Twitter Bot in Python, we will use Tweepy, a package that provides a very convenient way to use the Twitter API.

## Creating Twitter API Authentication Credentials
The Twitter API requires that all requests use OAuth to authenticate. So you need to create the required authentication credentials to be able to use the API. These credentials are four text strings:

- Consumer key
- Consumer secret
- Access token
- Access secret

If you already have a Twitter user account, then follow these steps to create the key, token, and secrets. Otherwise, you have to sign up as a Twitter user before proceeding.

### Step 1: Apply for a Twitter Developer Account
Go to the [Twitter developer](https://developer.twitter.com/en) site to apply for a developer account. Here, you have to select the Twitter user responsible for this account. It should probably be you or your organization. Here’s what this page looks like:

In this case, I chose to use my own account, @bhatia_mehar.

Twitter then requests some information about how you plan to use the developer account, as showed below:

You have to specify the developer account name and whether you are planning to use it for personal purpose or for your organization.

### Step 2: Create an Application
Twitter grants authentication credentials to apps, not accounts. An app can be any tool or bot that uses the Twitter API. So you need to register your an app to be able to make API calls.

To register your app, go to your [Twitter apps page](https://developer.twitter.com/en/portal/projects-and-apps) and select the Create an app option.

You need to provide the following information about your app and its purpose:

- **App name**: a name to identify your application (such as examplebot)
- **Application description**: the purpose of your application (such as an example bot for a Python article)
- **Your or your application’s website URL**: required, but can be your personal site’s URL since bots don’t need a URL to work
- **Use of the app**: how users will use your app (such as This app is a bot that will automatically respond to users)

### Step 3: Create the Authentication Credentials

To create the authentication credentials, go to your Twitter apps page. Here’s what the Apps page looks like:

Here you’ll find the Details button of your app. Clicking this button takes you to the next page, where you can generate the credentials.

By selecting the Keys and tokens tab, you can generate and copy the key, token, and secrets to use them in your code:

After generating the credentials, save them in the ``config.yaml`` file to later use them in your code.