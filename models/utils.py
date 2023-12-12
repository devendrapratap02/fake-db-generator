from .schema import DbColumn
from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
)


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