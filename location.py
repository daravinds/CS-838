import nltk
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from nltk.corpus import stopwords
import pdb
import re
import os


stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",
              "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
              'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
              'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll",
              'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
              'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
              'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
              'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
              'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
              'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
              'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
              'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd',
              'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn',
              "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn',
              "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't",
              'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't",
              "mr", "ms", "the"]


def get_previous_word(word, line):
    index = line.index(word)
    if index == 0:
        return None

    words_before = line[:index-1].split(" ")
    return words_before[-1]


def distance_from_mid(line, nthword):
    words = line.split()
    return abs(len(words)/2 - nthword)


def get_location_in_line(word, line):
    words = line.split(" ")
    return line.index(word)


def get_word_location_in_line(word, line):
    index = line.index(word)
    if index == 0:
        return 1

    words_before = line[:index - 1].split(" ")
    return len(words_before)


def get_next_word(word, line):
    index = line.index(word) + len(word) + 1
    return line[index:].split(" ")[0]


def is_all_caps(word):
    return 1 if word.isupper() else 0


def is_first_char_capitalised(word):
    words = word.split(" ")
    for w in words:
        if w[0].islower() or (not re.match("^[a-zA-Z ]*$", word)):
            return 0

    return 1


def is_in_bag_of_words(word):
    bag = ["US", "UK", "China", "India", "Brazil", "Russia"]
    return 1 if word in bag else 0


def is_first_word_word(word, line):
    return get_location_in_line(word, line) == 0


def unwanted_words(word):
    for x in word:
        if not x.isalpha() and not x.isspace():
            return 0

    negative = ["Sunday", "Saturday", "Monday", "Tuesday","Wednesday", "Thursday", "Friday", "January", "February",
                "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
                "Airways", "Brazilian", "Russian", "British", "Indian", "German", "European", "Asian", "Chinese",
                "American", "Japanese", "United", "French", "Chinese"]

    return 0 if word in negative else 1


# def previous_word_direction(word, word_context):
#     prefixes = ('north', 'east', 'west', 'south', "central", "mid")
#     previous_word = get_previous_word(word, word_context)
#
#     if not previous_word:
#         return 0
#
#     return 1 if previous_word.lower().startswith(prefixes) else 0


def previous_word_direction(word, word_context):
    prefixes = ('north', 'east', 'west', 'south', "central", "mid")
    for prefix in prefixes:
        if prefix in word.lower():
            return 1
    return 0


def has_keywords_before(word, word_context):
    keywords = ["at", "in"]

    previous_word = get_previous_word(word, word_context)

    if not previous_word:
        return 0

    if previous_word in keywords:
        return 1

    previous_previous_word = get_previous_word(previous_word, word_context)
    if previous_previous_word:
        return 1 if previous_previous_word in keywords else 0

    return 0


def has_keywords_after(word, word_context):
    keywords = ["'s", "based", "region", "square", "country", "city", "town", "county", "creek", "avenue", "court", "block", "street", "block", "drive",
                "centre", "center", "ramp", "exit", "boulevard", "states", "kingdom"]
    next_word = get_next_word(word, word_context)

    if not next_word or next_word == '':
        return 0

    if next_word.lower() in keywords:
        return 1

    return 0


def contains_suffix(word):
    if " " in word:
        return 0
    suffixes = ('land', 'lands', 'berg', 'burg', 'shire', 'cester', 'States', "ville")

    # if word.endswith(suffixes):
    #     print "$"*100
    #     print word

    return 1 if word.endswith(suffixes) else 0


def contains_prefix(word):
    prefixes = ('Mr', 'Ms',)

    # if word.endswith(suffixes):
    #     print "$"*100
    #     print word

    return 1 if word.startswith(prefixes) else 0


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
        'VBZ': 4,
        'JJ': 5,
        'JJR': 5,
        'JJS': 5
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

    return 1 if tag[0][1] == 'NNP' or tag[0][1] == 'NN' or tag[0][1] == 'NNS' else 0
    # return 1 if tag[0][1] == 'NNP' or tag[0][1] == 'NN' else 0


def is_location(word):
    result = re.search('^<LOCATION>(.*)</LOCATION>$', word)
    return True if result else False


def process_word(word):
    # result = re.search('<LOCATION>(.*)</LOCATION>', word)
    # return result.group(1)
    return word.replace('<LOCATION>', '').replace('</LOCATION>','')


def is_noun_new(word, line):
    if len(word) <= 0: return 0
    tag = nltk.pos_tag(line.split())
    # return 1 if tag[0][1] == 'NNP' or tag[0][1] == 'NN' else 0

    # if tag[0][1] == 'NNP':
    #     print "$"*100
    #     print word
    for item in tag:
        if item[0] == word:
            if item[1] == 'NNP' or item[1] == 'NN' or item[1] == 'NNS':
                return 1
            else:
                return 0
    #return 1 if tag[0][1] == 'NNP' or tag[0][1] == 'NN' or tag[0][1] == 'NNS' else 0
    #i=10/0
    return 0



def get_pos_class_new(word, line):
    pos_nominal_value_map = {
        ',': 1,
        '.': 1,
        'CC': 1,
        'IN': 2,
        'POS': 2,
        'NN': 3,
        'NNP': 3,
        'NNS':3,
        'VB': 4,
        'VBD': 4,
        'VBG': 4,
        'VBN': 4,
        'VBP': 4,
        'VBZ': 4,
        'JJ': 5,
        'JJR': 5,
        'JJS': 5
    }
    if not word:
        return 0
    tag = nltk.pos_tag(line.split())
    for item in tag:
        if item[0] == word:
            return pos_nominal_value_map.get(item[1], 0)
    #i=10/0
    # return pos_nominal_value_map.get(tag[0][1], 0)
    return 0


def get_tags(line):
    return nltk.pos_tag(line.split())


def get_pos_from_tag(word, tag):
    pos_nominal_value_map = {
        ',': 1,
        '.': 1,
        'CC': 1,
        'IN': 2,
        'POS': 2,
        'NN': 3,
        'NNP': 3,
        'NNS': 3,
        'VB': 4,
        'VBD': 4,
        'VBG': 4,
        'VBN': 4,
        'VBP': 4,
        'VBZ': 4,
        'JJ': 5,
        'JJR': 5,
        'JJS': 5
    }
    for item in tag:
        if item[0] == word:
            return pos_nominal_value_map.get(item[1], 0)
    return 0


def is_noun_new_new(word, tag):
    for item in tag:
        if item[0] == word:
            if item[1] == 'NNP' or item[1] == 'NN' or item[1] == 'NNS':
                return 1
    return 0


def get_feature_vector(rows):
    feature_vector = [[0] for x in range(len(rows))]

    previous_sentence = ""
    previous_tags = None
    for i in range(len(rows)):
        word, word_context, nthword, sentence = rows[i][0], rows[i][1], rows[i][2], rows[i][3]
        if sentence == previous_sentence:
            current_tags = previous_tags
        else:
            current_tags = get_tags(sentence)
        cur_vector = feature_vector[i]

        # cur_vector[0] = word
        # cur_vector[1] = word_context
        cur_vector[0] = is_first_char_capitalised(word)
        # cur_vector.append(is_first_char_capitalised(word))
        cur_vector.append(has_keywords_before(word, word_context))
        cur_vector.append(has_keywords_after(word, word_context))
        cur_vector.append(is_noun_new_new(word, current_tags))
        cur_vector.append(contains_suffix(word))
        # cur_vector.append(contains_prefix(word))
        cur_vector.append(previous_word_direction(word, word_context))
        # cur_vector.append(is_all_caps(word))
        cur_vector.append(get_location_in_line(word, word_context))
        cur_vector.append(get_word_location_in_line(word, word_context))
        # cur_vector.append(distance_from_mid(sentence, nthword))
        cur_vector.append(nthword)

        # cur_vector.append(is_first_word_word(word, word_context))
        next_word = get_next_word(word, word_context)
        if next_word:
            # cur_vector.append(get_pos_from_tag(next_word, sentence))
            cur_vector.append(get_pos_from_tag(next_word, current_tags))
            next_next_word = get_next_word(next_word, word_context)
            if next_next_word:
                cur_vector.append(get_pos_from_tag(next_next_word, current_tags))
            else:
                cur_vector.append(0)
        else:
            cur_vector.append(0)
            cur_vector.append(0)

        previous_word = get_previous_word(word, word_context)
        if previous_word:
            cur_vector.append(get_pos_from_tag(previous_word, current_tags))
            previous_previous_word = get_previous_word(previous_word, word_context)
            if previous_previous_word:
                cur_vector.append(get_pos_from_tag(previous_previous_word, current_tags))
            else:
                cur_vector.append(0)
        else:
            cur_vector.append(0)
            cur_vector.append(0)

        cur_vector.append(unwanted_words(word))
        cur_vector.append(has_stop_words(word))
        # cur_vector.append(is_in_bag_of_words(word))
        # cur_vector.append(rows[i][2])

        previous_sentence = sentence
        previous_tags = current_tags
    return feature_vector


def print_correct_labels(predicted, correct, data, rows):
    print "Correct Labels"
    count =0
    c = []
    for i in range(len(predicted)):
        if correct[i] == predicted[i] and correct[i]==1:
            print data[i][0] + "#######" + data[i][1] + "#####" + str(rows[i])
            count +=1
    # print c
    print count


def print_false_positive(predicted, correct, data, rows):
    print "\n"
    print "False positive"
    for i in range(len(predicted)):
        if predicted[i] == 1 and correct[i] != 1:
            print data[i][0] + "#######" + data[i][1]


def print_true_negative(predicted, correct, data, rows):
    print "\n"
    print "true negative"
    print len(data)
    print len(rows)
    for i in range(len(predicted)):
        if predicted[i] == 0 and correct[i] == 1:
            print data[i][0] + "#######" + data[i][1] + "#####" + str(rows[i])


def has_stop_words(word):
    for stop_word in stop_words:
        if stop_word in word:
            return True
    return False


def is_stop_words(word):
    return True if word in stop_words else False


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
    print_correct_labels(predicted_labels, v_labels, data, v_rows)
    print_false_positive(predicted_labels, v_labels, data, v_rows)
    print_true_negative(predicted_labels, v_labels, data, v_rows)
    print collections.Counter(predicted_labels)

    # pdb.set_trace()
    mean_scores["random-forest"] = scores.mean()

    print "-" * 100
    
    from sklearn import tree
    # clf2 = tree.DecisionTreeClassifier(criterion="entropy")
    clf2 = tree.DecisionTreeClassifier()
    clf2 = clf2.fit(rows, labels)
    scores = cross_val_score(clf2, rows, labels)
    mean_scores["decision-trees"] = scores.mean()
    predicted_labels = clf2.predict(v_rows)
    print "Decision Tree"
    print_correct_labels(predicted_labels, v_labels, data, v_rows)
    print_false_positive(predicted_labels, v_labels, data, v_rows)
    print_true_negative(predicted_labels, v_labels, data, v_rows)
    print collections.Counter(predicted_labels)

    # import graphviz
    # dot_data = tree.export_graphviz(clf2, out_file=None)
    # graph = graphviz.Source(dot_data)
    # graph.render("location")
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

    # print "-" * 100
    # clf4 = linear_model.LogisticRegression()
    # clf4 = clf4.fit(rows, labels)
    # scores = cross_val_score(clf4, rows, labels)
    # mean_scores["logistic-regression"] = scores.mean()
    # predicted_labels = clf4.predict(v_rows)
    # print "Logistic Regression"
    # print_correct_labels(predicted_labels, v_labels, data, v_rows)
    # print_false_positive(predicted_labels, v_labels, data, v_rows)
    # print_true_negative(predicted_labels, v_labels, data, v_rows)
    # print collections.Counter(predicted_labels)
    #
    # print "-" * 100

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


def get_row_and_label(word, line, nthword, sentence):
    # processed_word = word
    label = 0
    if is_location(word):
        # processed_word = process_word(word)
        #line = line.replace(word, processed_word)
        label = 1
    line = line.replace("</LOCATION>", "").replace("<LOCATION>", "")
    processed_word = process_word(word)
    row = [processed_word, line, nthword, sentence, label]
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
            # line = line.replace(",", "").replace(".", "")
            words = line.split(" ")
            num_words = len(words)
            for i in range(num_words):
                word = words[i]
                # if is_stop_words(word):
                #     continue
                mod_line = ""
                if i >= 2:
                    mod_line += " " + words[i-2]
                if i >=1:
                    mod_line += " " + words[i - 1]

                mod_line += " " + words[i]
                if i < num_words-1:
                    mod_line += " " + words[i+1]
                if i < num_words-2:
                    mod_line += " " + words[i+2]

                if is_invalid(word):
                    continue

                row, label = get_row_and_label(word, mod_line, i, line)
                rows.append(row)
                labels.append(label)

                if i < num_words-1:
                    next_word = words[i+1]
                    if is_invalid(next_word): # or is_stop_words(next_word.lower()) or is_stop_words(word.lower()):
                        continue
                    # if is_noun(next_word) or is_noun(word):
                    row, label = get_row_and_label(word + " " + next_word, mod_line, i, line)
                    rows.append(row)
                    labels.append(label)

    return rows, labels


"""
Millions of people were left homeless in Indonesia#L Aceh#L 's region following the earthquake and tsunami disaster in late December .
"""
def main():
    files = os.listdir("./mod_clean/")
    train = files[:-70] #random_subset(files, 50)
    test = files[-70:]#list(set(files) - set(test))

    # f = []
    train_rows, train_labels = get_rows_and_labels(train)


    # for row in train_rows:
    #     print row[0] + "#######" + get_next_word(row[0], row[1]) + "############" + row[1]

    print "validation"
    validation_rows, validation_labels = get_rows_and_labels(test)
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


import random
def random_subset(iterator, K ):
    result = []
    N = 0

    for item in iterator:
        N += 1
        if len( result ) < K:
            result.append(item)
        else:
            s = int(random.random() * N)
            if s < K:
                result[s] = item

    return result

if __name__ == '__main__':
    main()