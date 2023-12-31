import os
import pathlib
import shutil
from argparse import ArgumentParser

from sqlalchemy import (
    Column,
    Index,
    MetaData,
    Table,
    create_engine,
)
from sqlalchemy.engine import URL, Engine

from .models import (
    DbSchema,
    faker,
    get_column_type,
    ignore_exception,
    load_schema,
    logger,
)

sc:DbSchema
engine:Engine
metadata:MetaData


def base_setup(filepath):
    global engine
    global metadata
    global sc
    
    full_path = filepath if os.path.isabs(filepath) else os.path.join(os.getcwd(), filepath)
    sc = load_schema(full_path)
    
    engine = create_engine(URL.create(**sc.database.model_dump()), echo=sc.database.echo)
    
    metadata = MetaData()


def generate_tables():
    if not sc.tables:
        return

    for table_data in sc.tables:
        tt = Table(table_data.name, metadata, *[
                Column(
                    column_data.name,
                    get_column_type(column_data),
                    **column_data.options,
                ) 
                for column_data in table_data.columns
            ], *[
                Index(index.name, *index.columns) 
                for index in table_data.indexes
            ])
        
        with ignore_exception(Exception):
            tt.drop(engine)
        tt.create(engine)
        print(f"table {tt.name} successfully created")


def populate_data():
    if not sc.populate:
        return
    
    extras = {
        "engine": engine,
        "metadata": metadata,
    }
    with engine.connect() as conn:
        metadata.reflect(conn)
    
    table_length = max([len(t.name) for t in sc.populate])
    entry_length = max([len(str(t.count)) for t in sc.populate])
    
    log = logger(table_length, entry_length)
    
    for table in sc.populate:
        faker.unique.clear()
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
                log(table.name, index + 1, table.count)


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
            with engine.connect() as conn:
                metadata.reflect(conn)
                metadata.drop_all(conn)
                metadata.clear()
            
            generate_tables()
        if args.populate:
            populate_data()

if __name__ == "__main__":
    main()
