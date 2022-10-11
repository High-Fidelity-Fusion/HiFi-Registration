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
	$(MANAGE) test registration.tests.tests

test-e2e:
	$(MANAGE) migrate --settings=hifireg.settings.test
	$(MANAGE) shell -c "from registration.tests.cypress_test_seed import setup_cypress_test_data; setup_cypress_test_data()" \
	  --settings=hifireg.settings.test 
	./node_modules/.bin/concurrently -k --success=first -n cy,server --hide server \
	  "./node_modules/.bin/cypress run --config '{\"e2e\": {\"baseUrl\": \"http://localhost:8001\"}}'" \
	  "$(MANAGE) runserver 8001 --settings=hifireg.settings.test" \

test-full: test test-e2e

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
	$(MANAGE) shell -c "from registration.tests.manual_test_seed import setup_manual_test_data; setup_manual_test_data()"

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

https-tunnel:
	stunnel stunnel/dev_https.conf

https-run:
	HTTPS=1 ${MANAGE} runserver 8001
