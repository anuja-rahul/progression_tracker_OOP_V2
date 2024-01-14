"""
#!/usr/bin/env python3
backend validated data processing
progression_tracker_OOP_V2/handler.py
"""
import os
import uuid
from decorators import timer
from queries import QueryData
from validator import DataValidator
from cryptohandler import CryptoHandler
from datalogger import DataLogger

# TODO: Data entry method and get user stats unauthorized bin file generated.


class DataHandler:
    """
    Main class for handling user credentials, progress data, data processing, data reading and data writing.
    """

    salt_path = f"{os.getcwd()}/user_keys/"
    data_path = f"{os.getcwd()}/user_data/"
    progress_values = {
        1: "Progress",
        2: "Trailing",
        3: "Retriever",
        4: "Exclude"
    }

    def __init__(self, name: str, pass_marks: int = None, defer_marks: int = None, fail_marks: int = None,
                 password: str = "root", database: str = "local"):
        self.__name = name
        self.__password = password
        self.__uid = None
        self.__pass_marks = pass_marks
        self.__defer_marks = defer_marks
        self.__fail_marks = fail_marks
        self.__outcome = "undetermined"
        self.__db_con = QueryData(choice=database)
        self.__authentication = False
        self.__user_init = False
        self.__data_file = None
        self.__salt_file = None
        self.logger = DataLogger(name="HandleLogger", propagate=False)

        if self.__pass_marks is None or self.__defer_marks is None or self.__fail_marks is None:
            self.__validity = False
        else:
            student = DataValidator(self.__name, self.__pass_marks, self.__defer_marks, self.__fail_marks)

            if student.validity:
                self.__validity = True
            else:
                self.__validity = False

        self.init_env()
        self.init_user()

    @property
    def validity(self) -> bool:
        return self.__validity

    @property
    def authentication(self):
        return self.__authentication

    @classmethod
    @timer
    def init_env(cls) -> None:
        """creates necessary directories for user data files"""
        path_list = [DataHandler.salt_path, DataHandler.data_path]
        cls_logger = DataLogger(name="ClassDataHandler", propagate=False)

        for paths in path_list:
            try:
                os.mkdir(paths)
                cls_logger.log_info(f"[{paths}]  created.")
            except FileExistsError:
                cls_logger.log_info(f"Existing path found: [{paths}]")

    def init_user(self) -> None:
        """initiates and coordinates the methods assigning uid and password validation for new users"""

        self.assign_uid()
        self.check_password()

        if self.__authentication or not self.check_user_availability():
            self.__user_init = True

    def check_user_availability(self) -> bool:
        """
        search the database for existing users and sort new users and existing users
        :return: boolean value depending on user's existence
        """
        result = False
        temp_user_data = (self.__name,)
        sample_data = self.__db_con.execute(func=QueryData.read_user_data_fields(
            table_name='user_data',
            columns='name'
        ),
            output=True
        )
        for value in sample_data:

            if value == temp_user_data:
                result = True
            else:
                pass

        return result

    def check_password(self) -> None:
        """check and validate the passwords of existing users."""
        if self.check_user_availability():
            self.logger.log_info(f"[{self.__name}] existing user found.")
            sample_data = self.__db_con.execute(func=QueryData.read_user_specific_field(
                column='password',
                table_name='user_data',
                filter_expression=f"name='{self.__name}'"
            ),
                output=True
            )

            if self.__password == sample_data[0][0]:
                self.__authentication = True
                self.logger.log_info(f"User [{self.__name}] authentication successful.")

            else:
                self.logger.log_warning(f"User [{self.__name}] authentication unsuccessful.")
        else:
            pass

    def set_file_paths(self) -> None:
        """assign the paths for user data and bin files"""

        self.__data_file = f"{DataHandler.data_path}{self.__uid}.bin"
        self.__salt_file = f"{DataHandler.salt_path}{self.__uid}.bin"

    def assign_uid(self) -> None:
        """assigns a universally unique id for each new user.
        if the user already exists retrieve the existing uuid from the database"""
        if not self.check_user_availability():

            self.__uid = uuid.uuid4()
            self.set_file_paths()
            self.assign_cryptodata()

            data_entry = [f"'{self.__uid}'", f"'{self.__name}'", f"'{self.__password}'"]
            self.__db_con.execute(func=QueryData.create_row_query(
                table_name='user_data',
                data_list=data_entry
            ))

        else:
            sample_data = self.__db_con.execute(func=QueryData.read_user_specific_field(
                column='uid',
                table_name='user_data',
                filter_expression=f"name='{self.__name}'"
            ),
                output=True
            )

            if len(sample_data) > 0:
                self.__uid = sample_data[0][0]

        self.set_file_paths()

    def check_salt_data(self) -> bool:
        """
        check for existing salt bin files
        :return: boolean value depending on file's existence
        """
        current_files = os.listdir(DataHandler.salt_path)
        salt_file = f"{self.__uid}.bin"

        if salt_file in current_files:
            return True
        else:
            return False

    def assign_cryptodata(self) -> None:
        """assign necessary cryptographic data for new users"""

        if not self.check_salt_data():
            user = CryptoHandler(availability=False, password=self.__password)
            user.assign_salt()
            user.salt_to_bin(path=self.__salt_file)
            self.logger.log_info(f"[{self.__name}] - cryptodata assigned.")

        else:
            pass

    def progression_outcome(self) -> None:
        """calculate the user outcome based on validated marks"""

        progress, trailing, retriever, exclude = 0, 0, 0, 0

        if self.__pass_marks >= 100:
            if self.__pass_marks == 120:
                self.__outcome = DataHandler.progress_values[1]
                progress += 1
            else:
                self.__outcome = DataHandler.progress_values[2]
                trailing += 1

        elif self.__fail_marks >= 80:
            self.__outcome = DataHandler.progress_values[4]
            exclude += 1
        else:
            self.__outcome = DataHandler.progress_values[3]
            retriever += 1

        self.update_progression_stats(progress, trailing, retriever, exclude)
        self.logger.log_info("Progression stats updated.")

    def data_entry(self) -> list:
        """
        if validated, enters a new data set of user progress to the database
        :return: list of user progression data
        """

        if self.__user_init and self.__validity:
            self.progression_outcome()

            data_entry = [f"'{self.__uid}'", f"'{self.__pass_marks}'",
                          f"'{self.__defer_marks}'", f"'{self.__fail_marks}'", f"'{self.__outcome}'"]
            self.__db_con.execute(func=QueryData.create_row_query(
                table_name='user_progression',
                data_list=data_entry
            ))

            return [self.__name, self.__pass_marks, self.__defer_marks, self.__fail_marks, self.__outcome]
        else:
            return [self.__validity]

    def update_progression_stats(self, progress: int = 0, trailing: int = 0,
                                 retriever: int = 0, exclude: int = 0) -> None:
        """
        update the database according to new user progression stats.
        :param progress: progress count
        :param trailing: trailing count
        :param retriever: retriever count
        :param exclude: exclude count
        """

        sample_data = self.__db_con.execute(func=QueryData.read_all_queries(
            table_name='user_stats',
        ),
            output=True
        )

        if len(sample_data) == 0:
            filter_value = 0
        else:
            filter_value = sample_data[0][0]

            progress += sample_data[0][0]
            trailing += sample_data[0][1]
            retriever += sample_data[0][2]
            exclude += sample_data[0][3]

        progress_list = [progress, trailing, retriever, exclude]

        self.__db_con.execute(func=QueryData.delete_rows(
            table_name='user_stats',
            filter_expression=f"progress='{filter_value}'"
        ))

        self.__db_con.execute(func=QueryData.create_row_query(
            table_name='user_stats',
            data_list=progress_list
        ))

    def dump_to_bin(self, data_str: str = None) -> None:
        """
        Outputs a json file with given data.
        :param data_str: A string containing updated student progress data.
        :return: None
        """

        if data_str is None:
            data_str = self.generate_str()

        dump_user = CryptoHandler(availability=False, password=self.__password, logger_name="CryptoHandleLogger(ENC)")

        self.assign_cryptodata()

        dump_user.get_salt(path=self.__salt_file)
        self.logger.log_info("Key requested to dump data.")
        dump_user.generate_key()
        encrypted_data = dump_user.encrypt(data=data_str)
        dump_user.write_to_bin(file_name=self.__data_file, data=encrypted_data)

        self.logger.log_info(f"[{self.__name}] - Data bin encrypted.")

    def load_from_bin(self) -> str:
        """
        Loads a data string from a given bin file and returns it.
        :return: data_str: A dictionary containing student progress data.
        """

        try:
            load_user = CryptoHandler(availability=True, password=self.__password,
                                      logger_name="CryptoHandleLogger(DEC)")
            if self.check_salt_data():
                load_user.get_salt(path=self.__salt_file)
            else:
                raise Exception(f"{self.__salt_file} does not exists.")

            self.logger.log_info("Key requested to load data.")
            load_user.generate_key()
            encrypted_data = load_user.read_from_bin(file_name=self.__data_file)
            decrypted_data = load_user.decrypt(data=encrypted_data)
            self.logger.log_info(f"[{self.__name}] - Data bin decrypted.")

            return decrypted_data.decode()

        except FileNotFoundError as error:
            self.logger.log_error(str(error))

    def generate_str(self) -> str:
        """
        generated a string of user progression data from the database
        :return: string of progression data
        """

        sample_data = self.__db_con.execute(func=QueryData.read_user_specific_field(
            column="pass_marks, defer_marks, fail_marks, outcome",
            table_name='user_progression',
            filter_expression=f"uid='{self.__uid}'"
        ),
            output=True
        )

        user_progress = f"""
        Progress Data
        --------------
        Name: {self.__name}
        UID: {self.__uid}
        Data File: {self.__data_file}\n
        """
        for data in sample_data:
            user_progress = user_progress + f"\n        [pass:{data[0]} | defer:{data[1]} | fail:{data[2]} | " \
                                            f"outcome:{data[3]}]"

        self.logger.log_info("progress data string generated from database.")
        return user_progress

    def get_output(self) -> str:
        """
        if user is authenticated, coordinates the methods of data sorting, encrypting,
        writing, retrieving and decrypting
        :return: string of retrieved data
        """
        if self.__authentication:
            self.dump_to_bin(self.generate_str())
            data = self.load_from_bin()
            return data

    def get_user_data(self):
        return f"""
        name: {self.__name}
        password: {self.__password}
        """

    def __repr__(self) -> str:
        return f"{self.__name}, {self.__pass_marks}, {self.__defer_marks}, {self.__fail_marks}, {self.__outcome}"
