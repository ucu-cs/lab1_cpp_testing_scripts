#!/usr/bin/python3

import subprocess
import os
import random
import re
import math
from typing import List

WRONG_NUMBER_OF_ARGUMENTS = 1
WRONG_METHOD_NUMBER = 2
INPUT_FILE_OPEN_ERROR = 3
OUTPUT_FILE_OPEN_ERROR = 4
INPUT_FILE_READ_ERROR = 5
OUTPUT_FILE_WRITE_ERROR = 6

NON_EXISTING_FILE_NAME = "/tmp/lab1_cpp_test_non_existing_filename"
TEST_DIRECTORY_NAME = "lab1_cpp_test_no_permission"
MIN_METHODS_TO_IMPLEMENT = 3

INPUT_FILE_NAME = 'input.txt'
OUTPUT_FILE_NAME = 'output.txt'


class Test:
    def __init__(self, executable_path, input_file_generator, output_check_function):
        self._executable_path = executable_path
        self._functions_to_run = []
        self._sample_input_generator = input_file_generator
        self._output_check_function = output_check_function

    def add_test_function(self, function):
        self._functions_to_run.append(function)

    def run_tests(self) -> bool:
        tests_passed = True
        for function in self._functions_to_run:
            self._sample_input_generator(INPUT_FILE_NAME)
            if not function(self._executable_path):
                tests_passed = False

        print("Testing output...")
        for method_number in range(1, 20):
            print(f"Testing method {method_number}...")
            if os.path.exists(OUTPUT_FILE_NAME):
                os.remove(OUTPUT_FILE_NAME)
            input_data = self._sample_input_generator(INPUT_FILE_NAME)

            error_code = subprocess.call(
                [self._executable_path, str(method_number), INPUT_FILE_NAME, OUTPUT_FILE_NAME],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE)

            if error_code != 0 and error_code != WRONG_METHOD_NUMBER:
                input_file = open(INPUT_FILE_NAME, 'r')
                print(
                    f"Program returned error code {error_code} on input file with such input file:\n" + ''.join(
                        input_file.readlines()))
                input_file.close()
                return False
            elif error_code == WRONG_METHOD_NUMBER and method_number <= MIN_METHODS_TO_IMPLEMENT:
                print(
                    f"Wrong method number error code returned with method number {method_number}, while at least {MIN_METHODS_TO_IMPLEMENT} methods should have been implemented")
                return False
            elif error_code == WRONG_METHOD_NUMBER:
                return True

            if not self._output_check_function(input_data):
                return False
        return tests_passed


def test_wrong_arguments_error(binary_filename) -> bool:
    print("Testing with wrong arguments number...")
    try:
        for argc in (1, 2, 4, 5, 6):
            error_code = subprocess.call([binary_filename] + list(map(str, range(1, argc + 1))), stderr=subprocess.PIPE,
                                         stdout=subprocess.PIPE)
            if error_code != WRONG_NUMBER_OF_ARGUMENTS:
                print(
                    f"Wrong number of arguments error code {WRONG_NUMBER_OF_ARGUMENTS} not returned with {argc} arguments")
                return False
        return True
    except Exception as e:
        print(f"Could not run wrong argument return code test. Error: {e}")
        return False


def test_wrong_method_number(binary_filename) -> bool:
    print("Testing with wrong method number...")
    try:
        for method_n in (30, 100, 1000):
            error_code = subprocess.call([binary_filename, str(method_n), INPUT_FILE_NAME, OUTPUT_FILE_NAME],
                                         stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if error_code != WRONG_METHOD_NUMBER:
                print(
                    f"Wrong method number error code {WRONG_METHOD_NUMBER} not returned with method number {method_n}")
                return False
        return True
    except Exception as e:
        print(f"Could not run wrong method number return code test. Error: {e}")
        return False


def test_input_file_open_error(binary_filename) -> bool:
    print("Testing with unexisting input file...")
    try:
        error_code = subprocess.call([binary_filename, '1', NON_EXISTING_FILE_NAME, OUTPUT_FILE_NAME],
                                     stderr=subprocess.PIPE,
                                     stdout=subprocess.PIPE)
        if error_code != INPUT_FILE_OPEN_ERROR:
            print(f"Running with unexisting input file does not return error code {INPUT_FILE_OPEN_ERROR}")
            return False
        return True
    except Exception as e:
        print(f"Could not run input file open error return code test. Error: {e}")
        return False


def test_output_file_open_error(binary_filename) -> bool:
    print("Testing with output file that can not be open...")
    try:
        try:
            os.makedirs(TEST_DIRECTORY_NAME, 0000)
        except FileExistsError as _:
            os.chmod(TEST_DIRECTORY_NAME, 0000)
        error_code = subprocess.call([binary_filename, '1', INPUT_FILE_NAME, f'{TEST_DIRECTORY_NAME}/output.txt'],
                                     stderr=subprocess.PIPE,
                                     stdout=subprocess.PIPE)
        if error_code != OUTPUT_FILE_OPEN_ERROR:
            print(f"Error code {OUTPUT_FILE_OPEN_ERROR} not returned while trying to open a file wich is not permitted")
            return False
        return True
    except Exception as e:
        print(f"Could not run output file open error return code test. Error: {e}")
        return False


def _write_numbers_to_file(filename, numbers):
    f = open(filename, 'w')
    print(' '.join(map(str, numbers)), file=f)
    return numbers


def generate_input_file_with_integers(filename) -> List[int]:
    return _write_numbers_to_file(filename, list(range(-7, 9)) + [random.randint(-1000, 1000) for _ in range(10)])


def generate_input_file_with_floats(filename) -> List[float]:
    return _write_numbers_to_file(filename, [random.randint(-1000, 1000) / 100 for _ in range(20)])


def generate_input_file_multiple_lines(filename) -> List[str]:
    lines = []
    f = open(filename, 'w')
    for i in range(10):
        lines.append(' '.join(map(str, range(random.randint(1, 10)))) + '\n')
        f.write(lines[-1])
    f.close()
    return lines


# ================================= Variant 1 functions ====================================
var_1_generate_input = generate_input_file_with_integers


def var_1_check_output(input_numbers):
    f_in = open(OUTPUT_FILE_NAME, 'r')
    try:
        lines = f_in.readlines()
        output_sum = int(lines[0].strip())
        output_avg = float(lines[1].strip())
    except Exception as e:
        print("Error while reading output file. It is of wrong format...")
        return False

    if output_sum != sum(input_numbers) or not math.isclose(output_avg, sum(input_numbers) / len(input_numbers),
                                                            abs_tol=0.001):
        print(
            f"Wrong output file. \nInput numbers: {' '.join(map(str, input_numbers))}\nOutput sum: {output_sum}\nOutput average: {output_avg}")
        print(f"Proper values:\nSum: {sum(input_numbers)}\nAverage: {sum(input_numbers) / len(input_numbers)}")
        return False
    return True


# ================================= End of variant 1 functions =================================

# ================================= Variant 2 functions ====================================
var_2_generate_input = generate_input_file_with_floats


def var_2_check_output(input_numbers):
    f_in = open(OUTPUT_FILE_NAME, 'r')
    try:
        lines = f_in.readlines()
        output_sum = float(lines[0].strip())
        output_avg = float(lines[1].strip())
    except Exception as e:
        print("Error while reading output file. It is of wrong format...")
        return False

    if not math.isclose(output_sum, sum(input_numbers), abs_tol=0.001) or not math.isclose(output_avg,
                                                                                           sum(input_numbers) / len(
                                                                                               input_numbers),
                                                                                           abs_tol=0.001):
        print(
            f"Wrong output file. \nInput numbers: {' '.join(map(str, input_numbers))}\nOutput sum: {output_sum}\nOutput average: {output_avg}")
        print(f"Proper values:\nSum: {sum(input_numbers)}\nAverage: {sum(input_numbers) / len(input_numbers)}")
        return False
    return True


# ================================= End of variant 2 functions =================================


# ================================= Variant 3 functions ====================================
var_3_generate_input = generate_input_file_with_integers


def var_3_check_output(input_numbers):
    f_in = open(OUTPUT_FILE_NAME, 'r')
    try:
        lines = f_in.readlines()
        output_len_sum = int(lines[0].strip())
        output_avg_len = float(lines[1].strip())
    except Exception as e:
        print("Error while reading output file. It is of wrong format...")
        return False

    proper_len_sum = sum(map(len, map(str, input_numbers)))
    proper_avg_len = proper_len_sum / len(input_numbers)

    if output_len_sum != proper_len_sum or not math.isclose(output_avg_len, proper_avg_len, abs_tol=0.001):
        print(
            f"Wrong output file. \nInput numbers: {' '.join(map(str, input_numbers))}\nOutput length sum: {output_len_sum}\nOutput average length: {output_avg_len}")
        print(
            f"Proper values:\nLengths sum: {proper_len_sum}\nAverage length: {proper_avg_len}")
        return False
    return True

# ================================= End of variant 3 functions =================================

# ================================= Variant 4 functions ====================================
var_4_generate_input = generate_input_file_with_floats
var_4_check_output = var_3_check_output

# ================================= End of variant 4 functions =================================

# ================================= Variant 5 functions ====================================
var_5_generate_input = generate_input_file_multiple_lines


def var_5_check_output(input_file_lines):
    f_in = open(OUTPUT_FILE_NAME, 'r')
    try:
        lines = f_in.readlines()
        output_avg_lines_len = float(lines[0].strip())
        output_lines_count = int(lines[1].strip())

    except Exception as e:
        print("Error while reading output file. It is of wrong format...")
        return False

    # Check two different values cause the length of a line could encounter the \n or no
    if output_lines_count != len(input_file_lines) or (not math.isclose(output_avg_lines_len,
                                                                       sum(map(len, map(str, input_file_lines))) / len(
                                                                           input_file_lines), abs_tol=0.001) and 
                                                       not math.isclose(output_avg_lines_len,
                                                                       sum(map(lambda l: len(l) - 1, map(str, input_file_lines))) / len(
                                                                           input_file_lines), abs_tol=0.001)):
        print(
            f"Wrong output file. \nInput file: {''.join(input_file_lines)}\nOutput lines count: {output_lines_count}\nOutput average line length: {output_avg_lines_len}")
        print(
            f"Proper values: \nLines count: {len(input_file_lines)}\nAverage line length: {sum(map(len, map(str, input_file_lines))) / len(input_file_lines)}")
        return False
    return True


# ================================= End of variant 5 functions =================================

# ================================= Variant 6 functions ====================================
var_6_generate_input = generate_input_file_multiple_lines


def var_6_check_output(input_file_lines):
    f_in = open(OUTPUT_FILE_NAME, 'r')
    try:
        lines = f_in.readlines()
        output_length_mean = float(lines[0].strip())
        output_length_variance = float(lines[1].strip())

    except Exception as e:
        print("Error while reading output file. It is of wrong format...")
        return False

    words = []
    for line in input_file_lines:
        words += line.split()

    mean = sum(map(len, words)) / len(words)
    variance = sum(map((lambda x: (x - mean) ** 2), words)) / len(words)

    if not math.isclose(output_length_mean, mean, abs_tol=0.001) or not math.isclose(output_length_variance, variance,
                                                                                     abs_tol=0.001):
        print(
            f"Wrong output file. \nInput file: {''.join(input_file_lines)}\nOutput mean: {output_length_mean}\nOutput variance: {output_length_variance}")
        print(f"Proper values: \nMean: {mean}\nVariance: {variance}")
        return False
    return True


# ================================= End of variant 6 functions =================================

# ================================= Variant 7 functions ====================================
var_7_generate_input = generate_input_file_multiple_lines


def var_7_check_output(input_file_lines):
    f_in = open(OUTPUT_FILE_NAME, 'r')
    try:
        lines = f_in.readlines()
        output_first_word_count = int(lines[0].strip())

    except Exception as e:
        print("Error while reading output file. It is of wrong format...")
        return False

    words = []
    for line in input_file_lines:
        words += line.split()

    first_words_count = words.count(words[0])

    if output_first_word_count != first_words_count:
        print(
            f"Wrong output file. \nInput file: {''.join(input_file_lines)}\nOutput first words count: {output_first_word_count}")
        print(f"Proper values: \nWords count: {first_words_count}")
        return False
    return True


# ================================= End of variant 7 functions =================================


common_test_functions = [test_wrong_arguments_error, test_wrong_method_number, test_input_file_open_error,
                         test_output_file_open_error]

test_functions_by_variant = {
    1: [var_1_generate_input, var_1_check_output],
    2: [var_2_generate_input, var_2_check_output],
    3: [var_3_generate_input, var_3_check_output],
    4: [var_4_generate_input, var_4_check_output],
    5: [var_5_generate_input, var_5_check_output],
    6: [var_6_generate_input, var_6_check_output],
    7: [var_7_generate_input, var_7_check_output],
}


def main_test() -> int:
    if not os.path.exists('compile.sh'):
        print("./compile.sh does not exist..")
        return -1
    error_code = subprocess.call('./compile.sh', stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if error_code != 0:
        print(f"./compile.sh exited with code {error_code}, which is not 0")
        return -1

    executable_path = ""
    variant = 0
    try:
        for binary_filename in os.listdir('bin'):
            if match := re.match(r".*?(\d+)$", binary_filename):
                executable_path = 'bin/' + binary_filename
                variant = int(match.groups()[0])
                break
    except Exception as _:
        pass
    if not executable_path:
        print("Could not find a valid executable (with name in format '<some_name>_<var_number>' in bin directory")
        return -1

    if variant not in test_functions_by_variant.keys():
        print(f"Invalid variant in binary name {variant}")
        return -1

    t = Test(executable_path, test_functions_by_variant[variant][0], test_functions_by_variant[variant][1])
    for f in common_test_functions:
        t.add_test_function(f)

    if variant not in test_functions_by_variant.keys():
        print(f"Invalid variant in binary name {variant}")
        return -1

    if t.run_tests():
        print("All tests passed successfully...")
        return 0
    else:
        return -1


if __name__ == '__main__':
    exit(main_test())
