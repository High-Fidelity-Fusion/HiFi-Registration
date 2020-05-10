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