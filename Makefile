MANAGE = python hifireg/manage.py

all: migrate style email run

clean:
	cd hifireg/registration/migrations && ls --ignore=__init__.py | xargs rm -rf
	$(MANAGE) shell -c "from tools import pgadmin; pgadmin.reset_db()"

disconnect:
	$(MANAGE) shell -c "from tools import pgadmin; pgadmin.terminate_conn()"

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

run: 
	$(MANAGE) runserver

super:
	$(MANAGE) createsuperuser

test:
	$(MANAGE) test registration.tests

shell:
	$(MANAGE) shell

style:
	python -c "import sass; sass.compile(dirname=('hifireg/registration/sass', 'hifireg/registration/static/css'), output_style='compressed', omit_source_map_url=False)"

email:
	python hifireg/tools/mjml.py hifireg/registration/templates/email/order.mjml hifireg/registration/templates/email/order.html

style-watch:
	npm run css-watch

format:
	black -S -l150 hifireg/registration

lint:
	pylint hifireg/registration

test-data: migrate
	$(MANAGE) shell -c "from registration.tests import setup_products; setup_products()"

settings:
	python -c "from hifireg.tools.setup import wget; wget('${SETTINGS_SECRET_URL}', 'hifireg/hifireg/settings/secret.py')"

settings-dev:
	python -c "from hifireg.tools import setup; setup.get_dev_settings('${SETTINGS_DEV_URL}', 'hifireg/hifireg/settings/developer.py')"

deploy: style email
	cp Pipfile.lock hifireg/Pipfile.lock
	cd hifireg && eb deploy

deploy-env:
	cd hifireg && eb setenv SETTINGS_SECRET_URL="${SETTINGS_SECRET_URL}"

deploy-init:
	cd hifireg && eb init

deploy-open:
	cd hifireg && eb open
