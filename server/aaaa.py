

def split_words():
    while True:
        words = raw_input("Please input the words:")
        if words == "":
            break
        else:
            words = words.split()
            print "word list:" + str(words)
            number_list = vowel_count(words)
            print "number list:" + str(number_list)
            sum = sum_number(number_list)
            print "sum:" + str(sum)


def vowel_count(word_list):
    vowel_count_list = []
    for word in word_list:
        vowel_count_list.append(len(word))
    return vowel_count_list


def sum_number(number_list):
    sum = 0
    for number in number_list:
        sum += number
    return sum


if __name__ == "__main__":
    split_words()