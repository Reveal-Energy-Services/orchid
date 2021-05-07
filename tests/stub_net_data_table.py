#
# This file is part of Orchid and related technologies.
#
# Copyright (c) 2017-2021 Reveal Energy Services.  All Rights Reserved.
#
# LEGAL NOTICE:
# Orchid contains trade secrets and otherwise confidential information
# owned by Reveal Energy Services. Access to and use of this information is 
# strictly limited and controlled by the Company. This file may not be copied,
# distributed, or otherwise disclosed outside of the Company's facilities 
# except under appropriate precautions to maintain the confidentiality hereof, 
# and may not be used in any way not expressly authorized by the Company.
#


import datetime as dt

import orchid

import option
import toolz.curried as toolz

# noinspection PyUnresolvedReferences
from System import DateTime, DBNull, Type
# noinspection PyUnresolvedReferences
from System.Data import DataTable, DataColumn


# The `dump_xxx` and `format_yyy` functions are diagnostic tools.
def dump_table(data_table):
    if len(data_table.Columns) == 0 and len(data_table.Rows) == 0:
        print('Empty data table')
        return

    dump_column_names(data_table)
    dump_rows(data_table)


def dump_column_names(data_table):
    print(format_header(data_table))


def format_header(data_table):
    prefix = f'{"".join([" "] * 8)}'
    suffix = ' |'
    result = ''.join(toolz.concatv([prefix], toolz.concat(toolz.map(format_column_name, data_table.Columns)), [suffix]))
    return result


def format_column_name(column):
    return format_text_in_column(column.ColumnName, column)


def format_column_width(column):
    if is_net_int(column) or is_net_double(column):
        return 8

    if is_net_string(column) or is_net_date_time(column):
        return 32

    raise KeyError(f'Cannot determine size of column {column.ColumnName}')


def dump_column_details(data_table):
    print('Column Details:')
    for c in data_table.Columns:
        print(f'    Name: {c.ColumnName}')
        print(f'    Type: {str(c.DataType)}')
        print(f'    Read-only: {c.ReadOnly}')
    print('')


def dump_rows(data_table):
    for row_no, row in enumerate(data_table.Rows):
        print(format_row(row_no, row, data_table.Columns))


# def format_row(row_no, row, columns):
#     result = (f'row {row_no: 4}'
#               f' | {format_row_value(maybe_row_value(row[0]), columns[0]):8}'
#               f' | {format_row_value(maybe_row_value(row[1]), columns[0]):8}'
#               f' | {format_row_value(maybe_row_value(row[2]), columns[0]):12}'
#               f' | {format_row_value(maybe_row_value(row[3]), columns[0]):32} |')
#     return result
def format_row(row_no, row, columns):
    prefix = f'row {row_no: 4}'
    suffix = ' |'
    formatted_row_values = toolz.pipe(
        columns,
        toolz.map(lambda c: (c, maybe_row_value(row[c]))),
        toolz.map(lambda i: (i[0], text_row_value(*i))),
        toolz.map(lambda i: format_row_value(*i)),
        toolz.map(str),
        list,
    )
    result = ''.join(toolz.concatv([prefix], formatted_row_values, [suffix]))

    return result


def maybe_row_value(value):
    if DBNull.Value.Equals(value):
        return option.NONE

    return option.Some(value)


@toolz.curry
def text_row_value(column, maybe_value):
    return maybe_value.map_or_else(format_some_value(column), lambda: 'Nothing')


@toolz.curry
def format_some_value(column, value):
    if is_net_int(column) or is_net_double(column) or is_net_string(column):
        return value

    if is_net_date_time(column):
        return value.ToString('o')

    raise TypeError(value)


@toolz.curry
def format_row_value(column, text_value):
    return format_text_in_column(text_value, column)


def format_text_in_column(text, column):
    return f' | {text:{format_column_width(column)}}'


def populate_data_table(table_data_dto):
    """
    Construct a .NET `DataTable` from a `TableDataDto` instance

    The `TableDataDto` has three fields. The `column_types` field is an iterable of Python types. The
    `table_data` type is an iterable of identically structured `dicts` For example,
        example_to_convert = [
            {'foo': 3, 'bar': 3.414, 'baz': 'abc', 'quux': dup.isoparse('3414-02-07T18:14:14Z')},
            {'foo': 2, 'bar': 2.718, 'baz': 'def', 'quux': dup.isoparse('2718-01-04T14:01:07Z')},
            {'foo': 1, 'bar': 1.414, 'baz': 'ghi', 'quux': dup.isoparse('1414-01-07T17:34:14Z')},
        ]
    Finally, the `rename_column_func` is a `Callable[string] -> string` that maps from the keys of the
    `dicts` in the `table_data` field to names (`string` instances) identifying the corresponding
    .NET `ColumnType`.

    Args:
        table_data_dto: The `TableDataDto` specifying the schema and contents of the .NET `DataTable` to
        create.

    Returns:
        The .NET DataTable whose column names are generated by the `rename_column_func`, whose column types
        correspond to the Python types in `column_types`, and whose "cells" correspond to the values in the
        `dicts` in `table_data`.
    """
    if len(table_data_dto.table_data) == 0:
        return DataTable()

    result = toolz.pipe(
        DataTable(),
        add_data_table_columns(table_data_dto),
        add_data_table_rows(table_data_dto),
    )
    return result


@toolz.curry
def add_data_table_columns(data_table_dto, data_table):
    net_column_names = list(toolz.map(data_table_dto.rename_column_func, toolz.first(data_table_dto.table_data)))
    net_column_types = list(toolz.map(make_data_column_type, data_table_dto.column_types))
    for net_column_name, net_column_type in zip(net_column_names, net_column_types):
        new_column = make_data_table_column(net_column_name, net_column_type)
        data_table.Columns.Add(new_column)
    return data_table


def make_data_column_type(python_type):
    mapper = {int: 'System.Int32',
              float: 'System.Double',
              str: 'System.String'}
    try:
        return Type.GetType(mapper[python_type])
    except KeyError:
        if python_type == dt.datetime:
            return Type.GetType('System.DateTime')
        raise


def make_data_table_column(net_column_name, net_column_type):
    new_column = DataColumn()
    new_column.ColumnName = net_column_name
    new_column.DataType = net_column_type
    new_column.ReadOnly = True
    return new_column


# An example of a callable to convert a sequence of `str` "tags" to .NET column names
# @toolz.curry
# def data_tag_to_net_column_name(data_name):
#     mapper = {'foo': 'Foo',
#               'bar': 'Bar',
#               'baz': 'Baz', }
#     try:
#         return mapper[data_name]
#     except KeyError:
#         if data_name == 'quux':
#             return "Quark"
#         raise

@toolz.curry
def add_data_table_rows(data_table_dto, data_table):
    for row_data in toolz.map(toolz.valmap(option.maybe), data_table_dto.table_data):
        net_row_data = toolz.keymap(data_table_dto.rename_column_func, row_data)
        new_row = make_data_table_row(net_row_data, data_table)
        data_table.Rows.Add(new_row)
    return data_table


def make_data_table_row(row_data, data_table):
    data_table_row = data_table.NewRow()
    for net_column_name, perhaps_cell_value in row_data.items():
        if not is_net_date_time(data_table.Columns[net_column_name]):
            data_table_row[net_column_name] = perhaps_cell_value.unwrap_or(DBNull.Value)
        else:
            # noinspection PyUnresolvedReferences
            data_table_row[net_column_name] = perhaps_cell_value.map_or(orchid.net_quantity.as_net_date_time,
                                                                        DBNull.Value)
    return data_table_row


@toolz.curry
def is_net_column_of_type(net_type_name, net_column):
    return str(net_column.DataType) == net_type_name


is_net_int = is_net_column_of_type('System.Int32')
is_net_double = is_net_column_of_type('System.Double')
is_net_string = is_net_column_of_type('System.String')
is_net_date_time = is_net_column_of_type('System.DateTime')
