pmgbilltracker
==============

Bill Tracking Application for the Parliamentary Monitoring Group.


SETUP FOR LOCAL ENVIRONMENT:
-----------------------
To run this application in your local environment, using the builtin Flask dev-server:

1. Install the required packages:

    `sudo pip install Flask`
    `sudo pip install Flask-SQLAlchemy`
    `sudo pip install Flask-WTF==0.8.4`
    `sudo pip install Flask-Admin`
    `sudo pip install simplejson`

2. Navigate to the application folder in your terminal and run the dev server:

    `cd pmgbilltracker`
    `python runserver.py`

The application should now be running at `http://localhost:5000/`


DEPLOY INSTRUCTIONS:
-----------------------
To deploy this application to an Ubuntu 13.04 instance on AWS EC2:

1. Install fabric to handle deployment:

    `sudo pip install fabric`

2. Save the ssh key for the instance as `aws_code4sa.pem` in your `~/.ssh` directory.

3. Edit the `env.hosts` variable for the staging environment in fabfile.py to point to the correct instance.

4. Navigate into the application folder and run the server setup and deploy scripts:

    `cd pmgbilltracker`
    `fab staging setup`
    `fab staging deploy`

More details about setup and deployment can be found in fabfile.py, the script that fabric runs when it deploys the site.