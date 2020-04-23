# High Fidelity Registration
A dance registration system for anarchists.

## Django setup
- Dependencies: python3.8 & pipenv
- Run `pipenv sync` to install python dependencies
- TODO: add more details for setup

## Bulma setup:
- Dependencies: npm
- Install nvm (node version manager) -- https://github.com/nvm-sh/nvm
- Install Node using `nvm install --lts` or `nvm install node` (for LTS or latest versions respectively)
- Run `npm install` to install dependencies from `package.json`

## Generate Bulma custom css:
- Run `npm run build-css` or `make style`
- The css will be placed into `hifireg/registration/static/css`

## Test Data
Setup products test data by running:
1. `make shell`
1. `from registration.tests import setup_products`
1. `setup_products()`
