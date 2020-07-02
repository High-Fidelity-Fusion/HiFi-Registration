import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from hifireg import settings


def get_db_conn(db_name):
    database = settings.database
    conn = psycopg2.connect(
        host=database['HOST'],
        port=database['PORT'],
        database=db_name,
        user=database['USER'],
        password=database['PASSWORD'])
    return conn

def get_simple_cursor():
    conn = get_db_conn("postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # turn off transactions
    return conn.cursor()

def terminate_conn(db_name=settings.database['NAME']):
    cursor = get_simple_cursor()
    cursor.execute(f"select pg_terminate_backend (pg_stat_activity.pid) from pg_stat_activity where pg_stat_activity.datname = '{db_name}'")

def reset_db(db_name=settings.database['NAME']):
    cursor = get_simple_cursor()

    if(settings.DEBUG != True):
        print(f'You are NOT in debug mode! Type the name of the database ("{db_name}")to confirm:')
        if(input() != db_name):
            print("Aborted.")
            exit()

    cursor.execute(f"DROP DATABASE {db_name};")
    cursor.execute(f"CREATE DATABASE {db_name};")
