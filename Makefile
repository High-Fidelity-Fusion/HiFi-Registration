MANAGE = python hifireg/manage.py

all: style migrate run
clean_migrate: clean migrate
clean_run: clean migrate run

clean:
	cd hifireg/registration/migrations && ls --ignore=__init__.py | xargs rm -f
	$(MANAGE) shell -c "from tools import pgadmin; pgadmin.reset_db()"

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
	npm run css-build

style-watch:
	npm run css-watch

format:
	black -S -l150 hifireg/registration

lint:
	pylint hifireg/registration

test-data:
	$(MANAGE) shell -c "from registration.tests import setup_products; setup_products()"
