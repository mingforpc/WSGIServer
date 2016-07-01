from celery import Celery

app = Celery('tasks', backend="redis://172.17.0.4:6379/0", broker="redis://172.17.0.4:6379/0")

@app.task
def add(x, y):
    return x + y

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


# part 2

# 1
def eqChars(s, i):
    count = 0
    for char in s[i:]:
        if char == s[i]:
            count += 1
        else:
            break
    return count


def commpress(s):

    if len(s) == 1:
        return s + "1"

    count = eqChars(s, 0)
    s = s[0] + str(count) + commpress(s[count: len(s)])

    return s


# 2
def get_minimum(integer_list):
    length = len(integer_list)
    if length == 1:
        return integer_list[0]
    else:
        mid = length/2
        a = get_minimum(integer_list[0:mid])
        b = get_minimum(integer_list[mid:length])
        return a if a < b else b


if __name__ == "__main__":
    print commpress("aaaasdwaddcxazcxc")