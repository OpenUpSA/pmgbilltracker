pmgbilltracker
==============

Bill Tracking Application for the Parliamentary Monitoring Group.

The project consists of two components: a frontend client application to demonstrate a user-facing website,
and a backend application that handles all of the application logic, and exposes the database through an API
and an admin interface.


SETUP FOR LOCAL ENVIRONMENT:
-----------------------
To run this application in your local environment, using the builtin Flask dev-server:

1. Install the required Python packages listed in *fabfile.py* under *install_dependencies()*.

2. Navigate to the application folder in your terminal and run the dev server. First for the backend application:

        cd pmgbilltracker
        python runserver_backend.py

3. Open a new terminal, and do the same for the frontend application:

        cd pmgbilltracker
        python runserver_frontend.py


The frontend application should now be running at `http://localhost:5000/`, and the backend at `http://localhost:5001/`.


DEPLOY INSTRUCTIONS:
-----------------------
To deploy this application to an Ubuntu 13.10 instance on AWS EC2:

1. Install fabric to handle deployment:

        sudo pip install fabric

2. Save the ssh key for the instance as `aws_code4sa.pem` in your `~/.ssh` directory.

3. Edit the `env.hosts` variable for the staging environment in fabfile.py to point to the correct instance.

4. Navigate into the application folder and run the server setup and deploy scripts:

        cd pmgbilltracker
        fab staging install_dependencies
        fab staging configure
        fab staging deploy_backend
        fab staging deploy_frontend

More details about setup and deployment can be found in fabfile.py, the script that fabric runs during deployment.