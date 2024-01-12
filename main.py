"""
#!/usr/bin/env python3
user data input and output
progression_tracker_OOP_V2/main.py
"""
from handler import DataHandler
from datalogger import DataLogger
import click

data_logger = DataLogger(name="MainLogger", propagate=True)
databases = {
    "l": "local",
    "f": "foreign"
}
choices = list(databases.keys())


@click.group()
def main_method():
    pass


@click.command()
@click.option("--name", "-n", prompt="Enter your name", help="Name of the user", type=str, required=True)
@click.option("--password", "-pw", prompt="Enter your password", help="user password",
              type=str, required=False, default=None)
@click.argument("database", type=click.Choice(choices), default="l", required=False)
def add_user(name, password, database) -> None:
    """
    adds a new user
    :param name: username
    :param password: preferred password
    :param database: local or foreign [l/f]
    """
    try:
        user = DataHandler(name=name, password=password, database=databases[database])
        print(user.get_user_data())
        if user.authentication:
            print("\nUser added to the database !\n")
        else:
            print("\nCannot add user \nusername already exists !\n")

    except Exception as error:
        data_logger.log_critical(f"{error}")


@click.command()
@click.option("--name", "-n", prompt="Enter your name", help="Name of the user", type=str, required=True)
@click.option("--pass_marks", "-p", prompt="Enter your pass marks", help="pass marks", type=int, required=True)
@click.option("--defer_marks", "-d", prompt="Enter your defer marks", help="defer marks", type=int, required=True)
@click.option("--fail_marks", "-f", prompt="Enter your fail marks", help="fail marks", type=int, required=True)
@click.option("--password", "-pw", prompt="Enter your password", help="user password",
              type=str, required=False, default=None)
@click.argument("database", type=click.Choice(list(databases.keys())), default="l", required=False)
def add_marks(name: str, pass_marks: int, defer_marks: int, fail_marks: int, password: str, database: str) -> None:
    """
    add new user data entries to the database
    :param name: username
    :param pass_marks: pass marks
    :param defer_marks: defer marks
    :param fail_marks: fail marks
    :param password: user password
    :param database: local or foreign [l/f]
    """
    try:
        user = DataHandler(name=name, pass_marks=pass_marks, defer_marks=defer_marks, fail_marks=fail_marks,
                           password=password, database=databases[database])
        entry = user.data_entry()
        if len(entry) == 1:
            if not entry[0]:
                print(f"\nRecheck your inputs !\n")
            else:
                print(f"\nIncorrect password !\n")
        else:
            print(f"\n{entry}\nEntry successful !\n")

    except Exception as error:
        data_logger.log_critical(f"{error}")


@click.command()
@click.option("--name", "-n", prompt="Enter your name", help="Name of the user", type=str, required=True)
@click.option("--password", "-pw", prompt="Enter your password", help="user password",
              type=str, required=False, default=None)
@click.argument("database", type=click.Choice(list(databases.keys())), default="l", required=False)
def get_progress(name, password, database) -> None:
    """
    outputs the stored user progression data
    :param name: username
    :param password: user password
    :param database: local or foreign [l/f]
    :return: string of user progression data
    """
    try:
        user = DataHandler(name=name, password=password, database=databases[database])
        progress_data = user.get_output()
        if progress_data is None:
            print(f"\nIncorrect password !\n")
        else:
            print(f"{progress_data}\n\n")

    except Exception as error:
        data_logger.log_critical(f"{error}")


@click.command()
def get_stats() -> None:
    """gets the statistics of all user progression data"""
    print(f"\nI'm still working on this function.\n")


main_method.add_command(add_user)
main_method.add_command(add_marks)
main_method.add_command(get_progress)
main_method.add_command(get_stats)

if __name__ == "__main__":
    main_method()
