Yelp's Academic Dataset Examples
================================

We're providing three examples for use with the dataset available at
[http://www.yelp.com/academic_dataset]. They all depend on
[mrjob][https://github.com/Yelp/mrjob] and python 2.6.

Samples
------------

 - category\_predictor: Given some text, predict likely
   categories. For example:

    python category_predictor/predict.py category_predictor.json "bacon donut"
    > Category: "Food" - 82.66% chance
    > Category: "Restaurants" - 16.99% chance
    > Category: "Donuts" - 0.12% chance
    > Category: "Basque" - 0.02% chance
    > Category: "Spanish" - 0.02% chance

 - review\_autopilot: Use a markov chain to finish a review. For
   example:

	python review_autopilot/generate.py Food 'They have the best'
	> They have the best coffee is good food was delicious cookies and
	> a few friends i think they make this

 - positive\_category\_words: See the Yelp engineering blog for
   details about this example. In short, it generates positivity
   scores for words either globally or per-category.

Basic set-up
------------

You can use any of mjrob's runner with these examples, but we'll focus
on the local and emr runner (if you have access to your own hadoop
cluster, check out the mrjob docs for instructions on how to set this
up).

Local mode couldn't be easier:

    # this step will take a VERY long time
    python review_autopilot/autopilot.py yelp_academic_dataset.json > autopilot.json

    # this should be instant
	python review_autopilot/generate.py Food 'They have the best'
	> hot dogs ever

Waiting a long time is kind of lame, no? Let's try the same thing
using EMR.

First off, you'll need an aws\_access\_key and an
aws\_secret\_access\_key. You can get these from the AWS console
(you'll need to sign up for an AWS developer account and enable s3 /
emr usage, if you haven't already).

Create a simple mrjob.conf file, like this:

    runners:
	  emr:
	    aws_access_key_id: YOUR_ACCESS_KEY
		aws_secret_access_key: YOUR_SECRET_KEY

Now that that's done, you can run the autopilot script on EMR.

    # WARNING: this will cost you roughly $2 an hour
	python review_autopilot/autopilot.py --num-ec2-instances 10 --ec2-instance-type c1.medium -v --runner emr yelp_academic_dataset.json


You can save money (and time) by re-using jobflows and uploading the
dataset to a person, private s3 bucket - check out the mrjob docs for
instructions on doing this.
