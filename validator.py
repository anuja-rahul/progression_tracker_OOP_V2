"""
#!/usr/bin/env python3
backend data validation
progression_tracker_OOP_V2/validator.py
"""
from datalogger import DataLogger


class DataValidator:
    """
    Validates all the marks entered by user.
    """

    valid_range = list(range(0, 140, 20))

    def __init__(self, name: str, pass_marks: int, defer_marks: int, fail_marks: int):
        self.__name = name
        self.__pass_marks = pass_marks
        self.__defer_marks = defer_marks
        self.__fail_marks = fail_marks
        self.__validity = False
        self.__marks_list = [self.__pass_marks, self.__defer_marks, self.__fail_marks]
        self.logger = DataLogger(name="ValidationLogger", propagate=True)

        if self.validate_type():
            if self.validate_range():
                if self.validate_total():
                    self.__validity = True
                    self.logger.log_info(f"[{self.__name}] - Marks validated.")

    @property
    def name(self) -> str:
        return self.__name

    @property
    def pass_marks(self) -> int:
        return self.__pass_marks

    @property
    def defer_marks(self) -> int:
        return self.__defer_marks

    @property
    def fail_marks(self) -> int:
        return self.__fail_marks

    @property
    def validity(self) -> bool:
        return self.__validity

    def validate_type(self) -> bool:
        """
        validate the data type of marks
        :return: boolean of type validity
        """
        type_validity = True
        for mark in self.__marks_list:
            if isinstance(mark, int):
                pass
            else:
                type_validity = False
                self.logger.log_error(f"({mark}) should be an integer.")

        return type_validity

    def validate_range(self) -> bool:
        """
        validate the range of marks
        :return: boolean of validity
        """
        validity = True
        for mark in self.__marks_list:
            if mark in DataValidator.valid_range:
                pass
            else:
                validity = False
                self.logger.log_warning(f"({mark}) is out of range.")
        return validity

    def validate_total(self) -> bool:
        """
        validate the total of marks
        :return: boolean of validity
        """
        if self.__pass_marks + self.__defer_marks + self.__fail_marks == 120:
            return True
        else:
            self.logger.log_warning(f"Sum of ({self.__pass_marks},{self.__defer_marks},{self.__fail_marks}) "
                                    f"must be 120.")
            return False

    def __repr__(self) -> str:
        return f"[{self.__name}, {self.__pass_marks}, {self.__defer_marks}, {self.__fail_marks}, {self.__validity}]"
