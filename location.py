import nltk
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
import pdb
import re
import os



def get_previous_word(word, line):
    index = line.index(word)
    if index == 0:
        return None

    words_before = line[:index-1].split(" ")
    return words_before[-1]


def get_location_in_line(word, line):
    words = line.split(" ")
    return line.index(word)


def get_next_word(word, line):
    index = line.index(word) + len(word) + 1
    return line[index:].split(" ")[0]


def is_all_caps(word):
    return 1 if word.isupper() else 0


def is_first_char_capitalised(word):
    words = word.split(" ")
    for w in words:
        if w[0].islower() or (not re.match("^[a-zA-Z]*$", word)):
            return 0

    return 1


def is_first_word_word(word, line):
    return get_location_in_line(word, line) == 0


def previous_word_direction(word, word_context):
    prefixes = ('north', 'east', 'west', 'south',)
    previous_word = get_previous_word(word, word_context)

    if not previous_word:
        return 0

    return 1 if previous_word.lower().startswith(prefixes) else 0


def has_keywords_before(word, word_context):
    keywords = ["at", "in"]

    previous_word = get_previous_word(word, word_context)

    if not previous_word or previous_word == '':
        return 0

    if previous_word in keywords:
        return 1

    return 0


def has_keywords_after(word, word_context):
    keywords = ["'s", "based", "region", "square", "country", "city", "town", "county", "creek", "avenue", "court", "block", "street", "block", "drive",
                "centre", "center", "ramp", "exit", "boulevard"]
    next_word = get_next_word(word, word_context)

    if not next_word or next_word == '':
        return 0

    if next_word.lower() in keywords:
        return 1

    return 0


def contains_suffix(word):
    if " " in word:
        return 0
    suffixes = ('land', 'berg', 'burg', 'shire', 'cester')

    # if word.endswith(suffixes):
    #     print "$"*100
    #     print word

    return 1 if word.endswith(suffixes) else 0


def get_pos_class(word):
    pos_nominal_value_map = {
        ',': 1,
        '.': 1,
        'CC': 1,
        'IN': 2,
        'POS': 2,
        'NN': 3,
        'NNP': 3,
        'VB': 4,
        'VBD': 4,
        'VBG': 4,
        'VBN': 4,
        'VBP': 4,
        'VBZ': 4
    }
    if not word:
        return 0
    tag = nltk.pos_tag([word])
    return pos_nominal_value_map.get(tag[0][1], 0)

def is_noun(word):
    if len(word) <= 0: return 0
    tag = nltk.pos_tag([word])
    # return 1 if tag[0][1] == 'NNP' or tag[0][1] == 'NN' else 0

    # if tag[0][1] == 'NNP':
    #     print "$"*100
    #     print word

    return 1 if tag[0][1] == 'NNP' else 0

def is_location(word):
    result = re.search('^<LOCATION>(.*)</LOCATION>$', word)
    return True if result else False


def process_word(word):
    # result = re.search('<LOCATION>(.*)</LOCATION>', word)
    # return result.group(1)
    return word.replace('<LOCATION>','').replace('</LOCATION>','')


def get_feature_vector(rows):
    feature_vector = [[0] for x in range(len(rows))]

    for i in range(len(rows)):
        word, word_context = rows[i][0], rows[i][1]
        cur_vector = feature_vector[i]

        # cur_vector[0] = word
        # cur_vector[1] = word_context
        cur_vector[0] = is_first_char_capitalised(word)
        cur_vector.append(is_first_char_capitalised(word))
        cur_vector.append(has_keywords_before(word, word_context))
        cur_vector.append(has_keywords_after(word, word_context))
        cur_vector.append(is_noun(word))
        cur_vector.append(contains_suffix(word))
        cur_vector.append(previous_word_direction(word, word_context))
        cur_vector.append(is_all_caps(word))
        cur_vector.append(get_location_in_line(word, word_context))
        cur_vector.append(is_first_word_word(word, word_context))
        next_word = get_next_word(word, word_context)
        if next_word:
            cur_vector.append(get_pos_class(next_word))
            next_next_word = get_next_word(next_word, word_context)
            if next_next_word:
                cur_vector.append(get_pos_class(next_next_word))
            else:
                cur_vector.append(0)
        else:
            cur_vector.append(0)
            cur_vector.append(0)

        previous_word = get_previous_word(word, word_context)
        if previous_word:
            cur_vector.append(get_pos_class(previous_word))
            previous_previous_word = get_previous_word(previous_word, word_context)
            if previous_previous_word:
                cur_vector.append(get_pos_class(previous_previous_word))
            else:
                cur_vector.append(0)
        else:
            cur_vector.append(0)
            cur_vector.append(0)


        # cur_vector.append(rows[i][2])

    return feature_vector


def print_correct_labels(predicted, correct, data):
    print "Correct Labels"
    count =0
    for i in range(len(predicted)):
        if correct[i] == predicted[i] and correct[i]==1:
            print data[i][0]
            count +=1
    print count


def print_false_positive(predicted, correct, data):
    print "\n"
    print "False positive"
    for i in range(len(predicted)):
        if predicted[i] == 1 and correct[i] != 1:
            print data[i][0]

def print_true_negative(predicted, correct, data):
    print "\n"
    print "true negative"
    for i in range(len(predicted)):
        if predicted[i] == 0 and correct[i] == 1:
            print data[i][0] + "#######" + data[i][1]


def trainiing(rows, labels, v_rows, v_labels, data):
    mean_scores = {}
    clf1 = RandomForestClassifier()
    # for row in rows:
    #     print row
    # for label in labels:
    #     print label
    clf1 = clf1.fit(rows, labels)
    scores = cross_val_score(clf1, rows, labels)
    predicted_labels = clf1.predict(v_rows)

    # print "#" * 100
    # for predicted_label in predicted_labels:
    #     print predicted_label

    print "###"*100
    import collections
    print collections.Counter(v_labels)
    correct=0

    print "Random forest"
    print_correct_labels(predicted_labels, v_labels, data)
    print_false_positive(predicted_labels, v_labels, data)
    print_true_negative(predicted_labels, v_labels, data)
    print collections.Counter(predicted_labels)

    # pdb.set_trace()
    mean_scores["random-forest"] = scores.mean()

    print "-" * 100
    
    from sklearn import tree
    clf2 = tree.DecisionTreeClassifier()
    clf2 = clf2.fit(rows, labels)
    scores = cross_val_score(clf2, rows, labels)
    mean_scores["decision-trees"] = scores.mean()
    predicted_labels = clf2.predict(v_rows)
    print "Decision Tree"
    print_correct_labels(predicted_labels, v_labels, data)
    print_false_positive(predicted_labels, v_labels, data)
    print_true_negative(predicted_labels, v_labels, data)
    print collections.Counter(predicted_labels)

    # print "-" * 100
    from sklearn import linear_model
    # clf3 = linear_model.LinearRegression()
    # clf3 = clf3.fit(rows, labels)
    # scores = cross_val_score(clf3, rows, labels)
    # mean_scores["linear-regression"] = scores.mean()
    # predicted_labels = clf3.predict(v_rows)
    # print "Linear model"
    # print_correct_labels(predicted_labels, v_labels, data)
    # print_false_positive(predicted_labels, v_labels, data)
    # print_true_negative(predicted_labels, v_labels, data)
    # print collections.Counter(predicted_labels)

    print "-" * 100
    clf4 = linear_model.LogisticRegression()
    clf4 = clf4.fit(rows, labels)
    scores = cross_val_score(clf4, rows, labels)
    mean_scores["logistic-regression"] = scores.mean()
    predicted_labels = clf4.predict(v_rows)
    print "Logistic Regression"
    print_correct_labels(predicted_labels, v_labels, data)
    print_false_positive(predicted_labels, v_labels, data)
    print_true_negative(predicted_labels, v_labels, data)
    print collections.Counter(predicted_labels)

    print "-" * 100

    # from sklearn import svm
    # clf5 = svm.SVC()
    # clf5 = clf5.fit(rows, labels)
    # scores = cross_val_score(clf5, rows, labels)
    # mean_scores["svm"] = scores.mean()
    # predicted_labels = clf5.predict(v_rows)
    # print "SVM"
    # print_correct_labels(predicted_labels, v_labels, data)
    # print_false_positive(predicted_labels, v_labels, data)
    # print_true_negative(predicted_labels, v_labels, data)
    # print collections.Counter(predicted_labels)


def is_invalid(word):
    invalid_list = [".", ",", ". ", "'", "", " "]
    return word in invalid_list


def get_row_and_label(word, line):
    # processed_word = word
    label = 0
    if is_location(word):
        # processed_word = process_word(word)
        #line = line.replace(word, processed_word)
        label = 1
    line = line.replace("</LOCATION>", "").replace("<LOCATION>", "")
    processed_word = process_word(word)
    row = [processed_word, line, label]
    return row, label


def get_rows_and_labels(files):
    rows = []
    labels = []

    for fname in files:
        if not fname.endswith(".txt"):
            continue

        with open("./mod/" + fname) as f:
            print fname
            s = f.read()

        lines = s.split("\n")

        for line in lines:
            words = line.split(" ")
            num_words = len(words)
            for i in range(num_words):
                word = words[i]
                if is_invalid(word):
                    continue

                row, label = get_row_and_label(word, line)
                rows.append(row)
                labels.append(label)

                if i < num_words:
                    next_word = words[i+1]
                    if is_invalid(next_word):
                        continue
                    row, label = get_row_and_label(word + " " + next_word, line)
                    rows.append(row)
                    labels.append(label)

    return rows, labels


"""
Millions of people were left homeless in Indonesia#L Aceh#L 's region following the earthquake and tsunami disaster in late December .
"""
def main():
    files = os.listdir("./mod/")
    # f = []
    train_rows, train_labels = get_rows_and_labels(files[:85])


    # for row in train_rows:
    #     print row[0] + "#######" + get_next_word(row[0], row[1]) + "############" + row[1]

    validation_rows, validation_labels = get_rows_and_labels(files[85:97])
    feature_vector = get_feature_vector(train_rows)
    # for vector in feature_vector:
    #     print vector
    # print "#####" + str(labels.count(1))
    validation_feature_vector = get_feature_vector(validation_rows)
    #
    # print "############# training rows"
    # for i in range(len(train_rows)):
    #     if train_labels[i] == 1:
    #         print train_rows[i][0] + "#######" + train_rows[i][1]
    #
    # print "#############validation rows"
    # for i in range(len(validation_rows)):
    #     if validation_labels[i] == 1:
    #         print validation_rows[i][0] + "#####################" + validation_rows[i][1]

    # print len(feature_vector)
    # print "training"
    trainiing(feature_vector, train_labels, validation_feature_vector, validation_labels, validation_rows)
    # for v in feature_vector:
    #     print v


if __name__ == '__main__':
    main()