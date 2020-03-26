all: migrate run

clean:
	cd registration/migrations && ls --ignore=__init__.py | xargs rm -f
	rm -f db.sqlite3

migrate:
	./manage.py makemigrations
	./manage.py migrate

run: 
	./manage.py runserver

super:
	./manage.py createsuperuser

clean_migrate: clean migrate

clean_run: clean migrate run
