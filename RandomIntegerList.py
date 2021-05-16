from random import randint
from bitarray import bitarray


def next_number(max_integer, numbers_found):
    while True:
        new_number = randint(1, max_integer)
        if not numbers_found[new_number]:
            numbers_found[new_number] = True
            return new_number


def write_random_integer_file(max_integer, number_of_integers, file_name):
    numbers_found = bitarray(max_integer + 1)
    with open(file_name, 'w') as file:
        for number_of_elements in range(number_of_integers):
            new_number = next_number(max_integer, numbers_found)
            if number_of_elements > 0:
                file.write("\n")
            file.write(str(new_number))


def sort_random_integer_file(max_integer, input_file_name, output_file_name):
    """
    Input: A file containing at most max_integer positive integers,
    each less than max_integer. It is a fatal error if any integer
    occurs twice in the input.
    Output: A sorted list in increasing order of the input integers
    Constraints: At most (roughly) a megabyte of storage is available in main memory.
    From: Programming Pearls, Chapter 1
    """
    numbers_found = bitarray(max_integer + 1)
    with open(input_file_name, 'r') as file:
        for line in file:
            numbers_found[int(line)] = True
    file.close()

    with open(output_file_name, 'w') as file:
        for number in range(1, max_integer):
            if numbers_found[number]:
                file.write(str(number) + "\n")
    file.close()


if __name__ == "__main__":
    n = 10 ** 7
    k = 10 ** 5
    write_random_integer_file(n, k, "testdata/randintlist.txt")
    sort_random_integer_file(n, "testdata/randintlist.txt", "testdata/sortedIntlist.txt")
