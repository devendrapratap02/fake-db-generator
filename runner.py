import os
import sys

from sqlalchemy import (
    Column,
    MetaData,
    Table,
    create_engine,
)
from sqlalchemy.engine import URL

from models import faker, get_column_type, load_schema

# load schema json 
path = sys.argv[1]
filename = path if os.path.isabs(path) else os.path.join(os.path.dirname(__file__), path)
sc = load_schema(filename)

# Set up connections between sqlalchemy and postgres db-api
engine = create_engine(URL.create(**sc.database.model_dump()))

# Instantiate metadata class
metadata = MetaData()

def generate_tables():
    if sc.tables:
        for table_data in sc.tables:
            tt = Table(table_data.name, metadata, *[
                    Column(
                        column_data.name,
                        get_column_type(column_data),
                        **column_data.options,
                    ) 
                    for column_data in table_data.columns
                ])

            tt.create(engine)
            print(f"table {tt.name} successfully created")


def populate_data():
    if sc.populate:
        extras = {
            "engine": engine,
            "metadata": metadata,
        }
        with engine.connect() as conn:
            metadata.reflect(conn)

        for table in sc.populate:
            tt = metadata.tables.get(table.name)
            with engine.begin() as conn:
                for index in range(1, table.count+1):
                    commons = {}
                    results = {}
                    for field in table.fields:
                        results[field.name], commons = faker.get(
                            field.generator, 
                            field.args, 
                            commons, **extras if field.db_access else {}
                        )
                        
                    conn.execute(tt.insert().values(**results))

                    print(f"\r{table.name: <15}| {index: <4} entries | {index*100//table.count}%", end="\r")
            print()

if __name__ == "__main__":
    generate_tables()
    populate_data()
