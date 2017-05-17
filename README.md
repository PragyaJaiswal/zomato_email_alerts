# zomato_email_alerts
Email alerts for negative reviews on Zomato. Checks for new reviews every Monday and Thursday and sends and email alert if negative reviews are present. 

Everything gets logged in MySQL tables under database 'zomato_alerts'. Access table 'LOGS' to look at the logs generated while fetching, dumping and processing reviews. 
Access table 'REVIEWS' to look at reviews dumped for the restaurant IDs mentioned in the config file. Reviews are uniquely identified by a hash and a processed tag identifies if a review has already been processed. Each time the script is run, reviews are processed incrementally and it is made sure that already processed reviews are neither processed again nor are taken into consideration for sending alerts.

The email alert tells the percentage of negative reviews present in all the reviews that have been processed. The body of the email contains how many reviews were processed, number of reviews that were classified as negative, and a few negative reviews.

## Dependency
* MySQL
  
  Please install and setup MySQL and use the username and password in the config file.

  Make sure mysql server is up and running before moving further.

## Update config file
* Get Zomato API key
* Get SendGrid API key
* Edit the config file and add the API keys
* Add/Delete Zomato Restaurant IDs, if desired.
* Edit the config file to change the email sender and recipient
* Edit the config file to add MySQL username and password

## Configure and setup the repository
### Unix

#### Run the following commands on a Unix Shell
* pip install virtualenv

Create a new virtual environment

* python -m virtualenv </path/to/virtualenv/virtualenvname>
* cd </path/to/virtualenv/virtualenvname>
* source bin/activate

Copy the cloned repository in the virtualenv folder just created using the following -

* cd <cloned_repository>/scripts

Copy the Sendgrid API key in the command below - 

* echo "export SENDGRID_API_KEY= '<YOUR_API_KEY>' " > sendgrid.env

<!-- Set up cronjob for periodically running the script. -->
<!-- Runs the script and checks for negative reviews every Monday and Thursday at 0000hrs -->
* crontab -e

  _Copy and paste the following in the editor that opens up after editing wherever required. -_
  
  MAILTO = ''

  0 0 * * 1,4 source </path/to/virtualenv/virtualenvname>/bin/activate

  0 0 * * 1,4 </path/to/virtualenv/virtualenvname>/bin/python </path/to/virtualenv/virtualenvname>/<cloned_repository>/scripts/get_reviews.py > /tmp/cron.log 2>&1

* sudo apt-get install python-pip python-dev libmysqlclient-dev
* pip install -r requirements.txt
* python get_reviews.py

### Windows
TODO

### MAC OS X
TODO

## Enhancements
* Fetch only new reviews from Zomato
* Update the database with new reviews only
* Improve the format of the SendGrid email body