from contextlib import contextmanager

from sqlalchemy import Date, ForeignKey, Integer, MetaData, Numeric, String, select
from sqlalchemy.engine import Engine

from .fake import BaseProvider, faker
from .schema import TableColumn


@contextmanager
def ignore_exception(*exceptions):
    try:
        yield
    except exceptions:
        pass

def logger(table_length, entry_length):
    def log(table_name, progress, total):
        print(f"\r{table_name: <{table_length}} | {progress: >0{entry_length}} entries | {progress*100//total}%", end="\r")
        if progress == total:
            print()
    
    return log

def get_column_type(column:TableColumn):
    type_name = column.type.name
    type_args = column.type.args
    match type_name:
        case "integer": 
            return Integer
        case "number": 
            return Numeric(**type_args)
        case "string": 
            return String(**type_args)
        case "date": 
            return Date
        case "foreign": 
            if isinstance(type_args, dict):
                name, options = type_args.pop("name"), type_args
            else:
                name, options = type_args, {}
            return ForeignKey(name, **options)
        case _: 
            raise Exception(f"No matched column type found {type_name}")

class DbRandomItem(BaseProvider):
    __provider__ = "db_random_item"
    
    def db_random_item(self, attribute:str, **kwargs):
        table_name, column_name = attribute.split(".")
        
        engine:Engine = kwargs.get("engine")
        metadata: MetaData = kwargs.get("metadata")
        table = metadata.tables.get(table_name)
        
        with engine.begin() as conn:
            st = conn.execute(select(table.c[column_name])).fetchall()
            out = self.generator.random.choice(st)[0]
        
        return out

class UniqueProvider(BaseProvider):
    __provider__ = "unique_item"
    
    def unique_item(self, *args):
        return faker.unique.random_from(*args)

faker.add_provider(DbRandomItem)
faker.add_provider(UniqueProvider)
