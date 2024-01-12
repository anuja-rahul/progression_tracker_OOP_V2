"""
#!/usr/bin/env python3
Backend SQL query handler
progression_tracker_OOP_V2/queries.py
"""
import mariadb
import sqlite3
from datalogger import DataLogger

env_logger = DataLogger(name="QueryInfoLogger", propagate=False)


class QueryData:
    """
    Main class for SQL (mariadb/sqlite3) query handling
    """

    # Change the info in this dictionary according to your preferred database(mariadb).
    alt_query = {
        "host": 'localhost',
        "user": 'db_user',
        "password": 'root',
        "database": 'progression_tracker_db_v2'
    }

    local_db = {
        "database": "progression_db.db"
    }

    def __init__(self, host: str = alt_query["host"], user: str = alt_query["user"],
                 password: str = alt_query["password"], database: str = alt_query["database"],
                 choice: str = "local", **kwargs):

        self.logger = DataLogger(name="QueryLogger", propagate=False)
        self.__host = host
        self.__user = user
        self.__password = password
        self.__database = database
        self.__choice = choice
        self.connect = sqlite3.connect(QueryData.local_db["database"])

        env_logger.logger.propagate = True
        if self.choice != "local":
            try:
                self.connect = mariadb.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                env_logger.log_info(f"Proceeding with [alternate] foreign database [mariadb].")

            except Exception as exception:
                env_logger.log_error(str(exception))
                env_logger.log_info("Proceeding with [default] local database [sqlite3].")

        else:
            self.logger.log_info("Proceeding with [default] local database [sqlite3].")

        self.cursor = self.connect.cursor()
        self.init_tables()
        super().__init__(**kwargs)

    @property
    def host(self) -> str:
        return self.__host

    @property
    def user(self) -> str:
        return self.__user

    @property
    def password(self) -> str:
        return self.__password

    @property
    def database(self) -> str:
        return self.__database

    @property
    def choice(self) -> str:
        return self.__choice

    @staticmethod
    def default_user_setup() -> str:
        """
        Query to initiate the  user_data table
        :return: user_data table SQL query
        """

        return """
        
        CREATE TABLE IF NOT EXISTS `user_data` ( 
        `uid` VARCHAR(200) NOT NULL , 
        `name` TEXT NOT NULL , 
        `password` VARCHAR(300) NOT NULL);
        """

    @staticmethod
    def default_user_progression_setup() -> str:
        """
        Query to initiate the user_progression table
        :return: user_progression table SQL query
        """
        return """

        CREATE TABLE IF NOT EXISTS `user_progression` ( 
        `uid` VARCHAR(200) NOT NULL , 
        `pass_marks` VARCHAR(200) NOT NULL , 
        `defer_marks` VARCHAR(200) NOT NULL , 
        `fail_marks` VARCHAR(200) NOT NULL ,
        `outcome` VARCHAR(200) NOT NULL); 
        
                """
        # ENGINE = MyISAM;

    @staticmethod
    def default_user_statistics_setup() -> str:
        """
        Query to initiate the user_stats table
        :return: user_stats table SQL query
        """
        return """

        CREATE TABLE IF NOT EXISTS `user_stats` ( 
        `progress` INT(200) NULL DEFAULT '0' , 
        `trailing` INT(200) NOT NULL DEFAULT '0' , 
        `retriever` INT(200) NOT NULL DEFAULT '0' , 
        `exclude` INT(200) NOT NULL DEFAULT '0' ); 
                        """

    def execute(self, func: any = None, output: bool = False) -> list:
        """
        Executes a SQL query based on user preference
        :param func: Specific SQL query
        :param output: boolean value of output choice (True or False)
        :return: if output is True, returns fetched results
        """

        if func is not None:
            self.cursor.execute(func)
            self.connect.commit()
            if output:
                return self.cursor.fetchall()
        else:
            self.logger.log_critical(f"param: func is not specified -> {func}")
            raise Exception(f"param: func is not specified -> {func}")

    def init_tables(self) -> None:
        """
        Initiates all the necessary data tables
        :return: None
        """
        self.cursor.execute(self.default_user_setup())
        self.cursor.execute(self.default_user_progression_setup())
        self.cursor.execute(self.default_user_statistics_setup())

    @staticmethod
    def read_all_queries(table_name: str) -> str:
        """
        Reads all queries of a given table
        :param table_name: preferred table name
        :return: list of all the queries on the table
        """

        return f"""
        SELECT *
        FROM {table_name};
        """

    @staticmethod
    def read_user_data_fields(table_name: str, columns: str) -> str:
        """
        Reads a specific column of a given table
        :param table_name: preferred table name
        :param columns: required column(s)
        :return: list of a selected column
        """

        return f"""
        SELECT {columns}
        FROM {table_name};
        """

    @staticmethod
    def read_user_specific_field(table_name: str, filter_expression: str, column: str) -> str:
        """
        Reads a specific value from a column of a given table using filter expressions
        :param table_name: preferred table name
        :param filter_expression: expression to filter out a specific value
        :param column: required column
        :return: tuple of a selected data
        """

        return f"""
        SELECT {column}
        FROM {table_name}
        WHERE {filter_expression};
        """

    @staticmethod
    def create_row_query(table_name: str, data_list: list) -> str:
        """
        Enter a row of data to a specified table
        :param table_name: preferred table name
        :param data_list: list of values to be entered as a row
        :return: None
        """

        values_string = ", ".join(map(str, data_list))

        return f"""
        INSERT INTO {table_name}
        VALUES ({values_string});
        """

    @staticmethod
    def update_rows_query(table_name: str, column_value_pair: str, filter_expression: str) -> str:
        """
        Update a row of a specified table
        :param table_name: preferred table name
        :param column_value_pair: column and the value required to be updated
        :param filter_expression: filter expression to isolate a specific value
        :return: None
        """

        return f"""
        UPDATE {table_name}
        SET {column_value_pair}
        WHERE {filter_expression};
        """

    @staticmethod
    def delete_rows(table_name: str, filter_expression: str) -> str:
        """
        Delete a specified row from a specified table
        :param table_name: preferred table name
        :param filter_expression: filter expression to isolate a specific row
        :return: None
        """

        return f"""
        DELETE FROM {table_name}
        WHERE {filter_expression};
        """

    @staticmethod
    def read_using_inner_join(table_columns: str, join_table_1: str, join_table_2: str,
                              common_column: str, table_filter_expression: str) -> str:
        """
        Select a unique value from a given pair of tables using
        inner join to match 2 common columns and by filtering out unnecessary data
        :param table_columns: column from which the data is to be retrieved
        :param join_table_1: preferred table 1 name
        :param join_table_2: preferred table 2 name
        :param common_column: column common to both table 1 and table 2
        :param table_filter_expression: filter expression to isolate a specific data
        :return: tuple of a selected data
        """

        return f"""
        SELECT {table_columns}
        FROM {join_table_1} INNER JOIN {join_table_2} 
        ON {join_table_1}.{common_column} = {join_table_2}.{common_column}
        WHERE {table_filter_expression};
        """
