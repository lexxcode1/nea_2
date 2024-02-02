"""
This file contains helper functions for the project
"""

from connector import connect

db = connect()
cur = db.cursor()


def table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database

    :param table_name: str Name of the table to check
    :return bool : True if the table exists, False otherwise
    """

    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")

    return cur.fetchone() is not None


def row_exists(table_name: str, row_id: int) -> bool:
    """
    Check if a row exists in the database

    :param table_name: str Name of the table to check
    :param row_id: int ID of the row to check
    :return bool : True if the row exists, False otherwise
    """

    return True


def valid_variable(var):
    return isinstance(var, tuple) and len(var) is 3 and isinstance(var[2], str)


def validate_types(variables: list[tuple] | tuple):
    """
    Validate the types of variables
    :param variables: list[tuple] in form (var, var_type, var_name)
    :return:
    """
    # If variables is a tuple, check if it is in the correct format
    if isinstance(variables, tuple):
        if not valid_variable(variables):
            raise ValueError('variables must be in the format (var, var_type, var_name)')
        variables = [variables]

    # Check if variables is a list
    if not isinstance(variables, list):
        raise TypeError('variables must be a list of tuples')

    # Check if variables are in correct format
    if False in [valid_variable(var) for var in variables]:
        raise ValueError('variables must be in the format (var, var_type, var_name)')

    for var, var_type, var_name in variables:
        # Check if the variable is the correct type
        if not isinstance(var, var_type):
            raise TypeError(f'{var_name} must be a {var_type.__name__}, not {type(var).__name__}')
