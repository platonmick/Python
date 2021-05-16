def swap(array, i, j):
    temp = array[i]
    array[i] = array[j]
    array[j] = temp


def permutations(n, elements):
    number_of_elements = len(elements)
    if n == 1:
        print(elements)
    else:
        for i in range(number_of_elements - n, number_of_elements):
            swap(elements, number_of_elements - n, i)
            permutations(n - 1, elements[0: number_of_elements])


if __name__ == "__main__":
    input_list = [0, 1, 2, 3]
    permutations(len(input_list), input_list)
