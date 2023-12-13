from sqlalchemy import Date, ForeignKey, Integer, MetaData, Numeric, String, select
from sqlalchemy.engine import Engine

from .fake import BaseProvider, faker
from .schema import DbColumn


def get_column_type(column:DbColumn):
    type_name = column.type.get("name")
    type_args = column.type.get("args")
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
            return ForeignKey(type_args)
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

faker.add_provider(DbRandomItem)
