# zomato_email_alerts
Email alerts for negative reviews on Zomato

cd scripts
echo "export SENDGRID_API_KEY='YOUR_API_KEY'" > sendgrid.env
echo "sendgrid.env" >> ../.gitignore
source ./sendgrid.env
