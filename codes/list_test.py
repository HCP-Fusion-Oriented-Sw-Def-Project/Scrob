
def test1():
    list1 = [1, 1, 2, 2, 3, 3, 3, 4, 5, 6]
    list2 = [1, 2, 3, 4, 5, 5, 6, 6]

    counter = 0
    total = len(list1) + len(list2)
    for i in range(len(list1)):
        for j in range(len(list2)):
            if list1[i] == list2[j] and list1[i] != -1 and list2[j] != -1:
                counter += 2
                list1[i] = -1
                list2[j] = -1

    print(counter / total)

test1()

