# High Fidelity Registration
This README contains the minimum information needed for a developer to setup the package.
For more complete information, see our setup instructions and onboarding guide here:
https://docs.google.com/document/d/1qdJ-26sYB21YMrn7ydTUSXP6XCWlehiwo_vOs1cUhM0/edit?usp=sharing

## Django setup
- Dependencies: python3.8 & pipenv
- Run `pipenv sync` to install python dependencies

## Bulma setup:
- Dependencies: npm
- Install nvm (node version manager)  https://github.com/nvm-sh/nvm
- Install Node using `nvm install lts` or `nvm install node` (for LTS or latest versions respectively)
- Run `npm install` to install dependencies from `package.json`

## Generate Bulma custom css:
- Run `npm run build-css` or `make style`
- The css will be placed into `hifireg/registration/static/css`

## Deploying via Elastic Beanstalk
https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html#python-django-deploy

### First Time Setup
Change directories into `./hifireg`.
- This is where all deployment actions take place.
- Anything above this directory is invisible to deployment.

Run `eb init -p python-3.7 hifireg` selecting reasonable options (probably the defaults):
- On your first run of `eb` you'll need to create some EB credentials.
- Choose the default region.
- Setup SSH...
- Create a local keypair with an identifiable name.

Run `eb create hifireg-env`.

Run `eb status`
- Replace the one entry of `ALLOWED_HOSTS` in your "secret.py" settings with the CNAME from `eb status`.
  (Make sure you update the remote copy of "secret.py" not just your local copy.)

Run `eb setenv SETTINGS_SECRET_URL="${SETTINGS_SECRET_URL}"`
- This will set the URL on the environment for your "secret.py" settings.

Deploying:
- Return to the top level directory and run `make deploy`
  (This task builds all of the necessary styling and bootstrapping for deploying)
- If you haven't modified style, email, or pipenv dependencies, you can run `make deploy-simple` for future deployments.
- Check out the running instance by running: `make deploy-open`

### Adding a New Deployer
Additional deployment machines can be setup by running `eb init`:
- A helper task has been added to make: `make deploy-init`
- (The instructions are un-tested).
- Since the application and environment are already setup, you shoudn't have to re-create them.
- New AWS access keys will need to be created for each new deployer.
  (https://console.aws.amazon.com/iam/home?region=us-west-2#/security_credentials)
- New SSH keys (generated locally) will need to be created for each new deployer.

### Setting up HTTPS for Beta Site
Follow these instructions using the "Terminate at the load balancer" method:
https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https.html
- These instructions are only useful for a beta site as it uses a self-signed certificate.
- This only needs to be done once.
- You'll need to setup `aws` cli tool.
- Use the web console to do this setup (instead of the *.config file)

### Setting up HTTPS for Production Site
TODO
