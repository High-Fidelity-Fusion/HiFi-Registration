MANAGE = python hifireg/manage.py

all: migrate run
clean_migrate: clean migrate
clean_run: clean migrate run

clean:
	cd hifireg/registration/migrations && ls --ignore=__init__.py | xargs rm -f
	rm -f db.sqlite3

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

run: 
	$(MANAGE) runserver

super:
	$(MANAGE) createsuperuser

test:
	$(MANAGE) test

shell:
	$(MANAGE) shell
	
style:
	npm run css-build

