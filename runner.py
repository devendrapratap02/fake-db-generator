import os
import sys

from models.fake import faker
from models.schema import load_schema
from sqlalchemy import (
    Column,
    MetaData,
    Table,
    create_engine,
)
from sqlalchemy.engine import URL

# load schema json 
path = sys.argv[1]
filename = path if os.path.isabs(path) else os.path.join(os.path.dirname(__file__), path)
sc = load_schema(filename)

# Set up connections between sqlalchemy and postgres db-api
engine = create_engine(URL.create(**sc.database.model_dump()))

# Instantiate metadata class
metadata = MetaData()

if sc.tables:
    for table_data in sc.tables:
        tt = Table(table_data.name, metadata, *[
                Column(
                    column_data.name,
                    column_data.get_type(),
                    **column_data.options,
                ) 
                for column_data in table_data.columns
            ])

        tt.create(engine)
        print(f"table {tt.name} successfully created")

if sc.populate:
    with engine.connect() as conn:
        metadata.reflect(conn)

    for table in sc.populate:
        tt = metadata.tables.get(table.name)
        with engine.begin() as conn:
            for _ in range(table.count):
                commons = {}
                results = {}
                for field in table.fields:
                    results[field.name], commons = faker.get(
                        field.generator, 
                        field.args, 
                        commons
                    )
                    
                conn.execute(tt.insert().values(**results))