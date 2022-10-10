# High Fidelity Registration
This README contains the minimum information needed for a developer to setup the package.
For more complete information, see our setup instructions and onboarding guide here:
https://docs.google.com/document/d/1qdJ-26sYB21YMrn7ydTUSXP6XCWlehiwo_vOs1cUhM0/edit?usp=sharing

## Django setup
- Dependencies: python3.8 & pipenv
- Run `pipenv sync` to install python dependencies

## Bulma setup:
- Add the bulma submodule: `git submodule update --init`
- Generate custom css: `make style`
- The css will be placed into `hifireg/registration/static/css`

## Running End-to-End tests with Cypress
- `npm install` (will take a while)
- `npm test`

## Deploying via Elastic Beanstalk
https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html#python-django-deploy

### First Time Setup
Change directory into `./hifireg`.
- This is where all deployment actions take place.
- Anything above this directory is invisible to deployment.

Run `eb init -p python-3.7 hifireg` selecting reasonable options (probably the defaults):
- On your first run of `eb` you'll need to create AWS credentials.
  (https://console.aws.amazon.com/iam/home?region=us-west-2#/security_credentials)
- Choose the default region.
- Setup SSH...
- Create a local keypair.

Run `eb create hifireg-env`.

Run `eb status`
- Replace the one entry of `ALLOWED_HOSTS` in your "secret.py" settings with the CNAME from `eb status`.
  (Make sure you update the remote copy of "secret.py" not just your local copy.)

Run `eb setenv SETTINGS_SECRET_URL="${SETTINGS_SECRET_URL}"`
- This will set the URL on the environment for your "secret.py" settings.
- Shortcut target: `make deploy-env`

Deploying:
- Return to the top level directory and run `make deploy`
  (This task builds all of the necessary styling and bootstrapping for deploying)
- Check out the running instance by running: `make deploy-open`

### Setting up IAM Deployer
You may choose to setup a non-root account with access to your AWS console:
https://console.aws.amazon.com/iam/home#/home

### Adding a New Deployer
Additional deployment machines can be setup:
- Change directory to `./hifireg` and run `eb init`.
- New AWS access keys will need to be created or distributed to each new deployer.
- Since the application and environment are already setup, you shoudn't have to re-create them.

### Setting up Domain name
Add a CNAME record mapping your subdomain 
(e.g. alpha.highfidelityfusion.com) 
to the name of your elastic beanstalk instance
(e.g. hifireg-env.eba-blahblah.us-west-2.elasticbeanstalk.com).

### Setting up HTTPS
Before you begin, make sure you've done the following:
- Make sure you have added a CNAME entry to your DNS for a domain that you control.
- Use AWS Certificate Manager to issue a certificate covering your domain:
  https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html#request-public-console

Then, follow these instructions using the "Terminate at the load balancer" method:
https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-elb.html
- Use the web console to do this setup (not the *.config file)
- Do not disable port 80 on the load balancer. The Django app is configured 
  to redirect this HTTP traffic to HTTPS requiring no configuration of Elastic Beanstalk.
