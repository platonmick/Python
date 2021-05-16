def swap(list, i, j):
    temp = list[i]
    list[i] = list[j]
    list[j] = temp

def permutations(n, list):
    numberOfElements = len(list)
    if n == 1:
        print(list)
    else:
        for i in range(numberOfElements - n, numberOfElements):
            swap(list, numberOfElements - n, i )
            permutations(n - 1, list[0 : numberOfElements])

if __name__ == "__main__":
    list = [0, 1, 2, 3]
    permutations(len(list), list)
