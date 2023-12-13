import os
import pathlib
import shutil
from argparse import ArgumentParser

from sqlalchemy import (
    Column,
    MetaData,
    Table,
    create_engine,
)
from sqlalchemy.engine import URL, Engine

from .models import DbSchema, faker, get_column_type, load_schema

sc:DbSchema
engine:Engine
metadata:MetaData

def base_setup(filepath):
    global engine
    global metadata
    global sc
    
    full_path = filepath if os.path.isabs(filepath) else os.path.join(os.getcwd(), filepath)
    sc = load_schema(full_path)
    
    engine = create_engine(URL.create(**sc.database.model_dump()))
    
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

def main():
    parser = ArgumentParser(prog="fdg", description="Fake Database Generator!!!")

    parser.add_argument("-c", "--create-table", action="store_true", dest="create", help="creates the database tables")
    parser.add_argument("-p", "--populate-data", action="store_true", dest="populate", help="start populating data in tables")

    parser.add_argument("-f", "--file", type=pathlib.Path, help="file path of schema")

    parser.add_argument("-d", "--download-schema", type=pathlib.Path, help="creates the example schema in the provided path")

    args = parser.parse_args()

    if not args.create and not args.populate and args.download_schema is None:
        parser.error("no arguments provided!!!")

    if (args.create or args.populate) and args.file is None:
        parser.error("the following arguments are required: -f/--file : file path of schema")

    if args.download_schema is not None:
        src_path = os.path.join(os.path.dirname(__file__), "data", "schema.json")
        dest_path = os.path.join(os.getcwd(), "schema.json")
        shutil.copyfile(src_path, dest_path)
    else:
        base_setup(args.file)
        
        if args.create:
            generate_tables()
        if args.populate:
            populate_data()
