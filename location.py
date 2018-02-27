import nltk
from sklearn.model_selection import cross_val_score
import pdb


def is_first_char_capitalised(word):
    return 1 if len(word) > 1 and word[0].isupper() else 0


def has_keywords_before(word, word_context):
    keywords = ["at", "in"]
    words = word_context.split(" ")
    word_index = words.index(word)

    if word_index == 0:
        return 0

    if words[word_index-1] in keywords:
        return 1

    return 0


def has_keywords_after(word, word_context):
    keywords = ["region", "square", "country", "city", "town", "county", "creek", "avenue", "court", "block", "street", "block", "drive",
                "centre", "center", "ramp", "exit", "boulevard"]
    words = word_context.split(" ")
    word_index = words.index(word)

    if word_index == len(words)-1:
        return 0

    if words[word_index + 1].lower() in keywords:
        return 1

    return 0


def is_noun(word):
    if len(word) <= 0: return 0
    tag = nltk.pos_tag([word])
    return 1 if tag[0][1] == 'NNP' or tag[0][1] == 'NN' else 0


def is_location(word):
    return 1 if "#L" in word else 0


def process_word(word):
    return word.replace("#L", "")


def get_feature_vector(rows):
    feature_vector = [[0] for x in range(len(rows))]
    labels = []

    for i in range(len(rows)):
        word, word_context = rows[i][0], rows[i][1]
        #word = process_word(crude_word)
        cur_vector = feature_vector[i]

        # cur_vector[0] = word
        cur_vector[0] = is_first_char_capitalised(word)
        # cur_vector.append(is_first_char_capitalised(word))
        cur_vector.append(has_keywords_before(word, word_context))
        cur_vector.append(has_keywords_after(word, word_context))
        cur_vector.append(is_noun(word))

        labels.append(is_location(word))

    return feature_vector, labels


def trainiing(rows, labels, v_rows, v_labels):
    from sklearn.ensemble import RandomForestClassifier
    mean_scores = {}
    clf1 = RandomForestClassifier()
    clf1 = clf1.fit(rows, labels)
    scores = cross_val_score(clf1, rows, labels)
    predicted_labels = clf1.predict(v_rows)

    correct=0
    for i in range(len(predicted_labels)):
        if v_labels[i] == predicted_labels[i]:
            correct+=1
    print correct
    print len(predicted_labels)
    pdb.set_trace()
    mean_scores["random-forest"] = scores.mean()

    # from sklearn import tree
    # clf2 = tree.DecisionTreeClassifier()
    # clf2 = clf2.fit(training_set, training_set_labels)
    # scores = cross_val_score(clf2, training_set, training_set_labels)
    # mean_scores["decision-trees"] = scores.mean()
    #
    # from sklearn import linear_model
    # clf3 = linear_model.LinearRegression()
    # clf3 = clf3.fit(training_set, training_set_labels)
    # scores = cross_val_score(clf3, training_set, training_set_labels)
    # mean_scores["linear-regression"] = scores.mean()
    #
    # clf4 = linear_model.LogisticRegression()
    # clf4 = clf4.fit(training_set, training_set_labels)
    # scores = cross_val_score(clf4, training_set, training_set_labels)
    # mean_scores["logistic-regression"] = scores.mean()
    #
    # from sklearn import svm
    # clf5 = svm.SVC()
    # clf5 = clf5.fit(training_set, training_set_labels)
    # scores = cross_val_score(clf5, training_set, training_set_labels)
    # mean_scores["svm"] = scores.mean()

"""
Millions of people were left homeless in Indonesia#L Aceh#L 's region following the earthquake and tsunami disaster in late December .
"""
def main():
    rows = [
        ["Millions", "Millions of people were left homeless in Indonesia#L Aceh#L region"],
        ["of", "Millions of people were left homeless in Indonesia#L Aceh#L region"],
        ["people", "Millions of people were left homeless in Indonesia#L Aceh#L region"],
        ["were", "Millions of people were left homeless in Indonesia#L Aceh#L region"],
        ["left", "Millions of people were left homeless in Indonesia#L Aceh#L region"],
        ["homeless", "Millions of people were left homeless in Indonesia#L Aceh#L region"],
        ["in", "Millions of people were left homeless in Indonesia#L Aceh#L region"],
        ["Indonesia#L", "Millions of people were left homeless in Indonesia#L Aceh#L region"],
        ["Aceh#L", "Millions of people were left homeless in Indonesia#L Aceh#L region"],
        ["region", "Millions of people were left homeless in Indonesia#L Aceh#L region"],

    ]
    import os
    rows = []
    files = os.listdir("/Users/cyn0/cs839/stanford/stanford-ner-2017-06-09/mod/")
    # f = []
    for fname in files[:400]:
        if not fname.endswith(".txt"):
            continue
        with open("/Users/cyn0/cs839/stanford/stanford-ner-2017-06-09/mod/" + fname) as f:
            print fname
            s = f.read()
        lines = s.split("\n")
        for line in lines:
            for word in line.split(" "):
                row = [word, line]
                rows.append(row)

    validation_rows = []
    for fname in files[400:]:
        if not fname.endswith(".txt"):
            continue
        with open("/Users/cyn0/cs839/stanford/stanford-ner-2017-06-09/mod/" + fname) as f:
            print fname
            s = f.read()
        lines = s.split("\n")
        for line in lines:
            for word in line.split(" "):
                row = [word, line]
                validation_rows.append(row)

    # for row in rows:
    #     print row
    feature_vector, labels = get_feature_vector(rows)
    validation_feature_vector, validation_labels = get_feature_vector(validation_rows)

    print len(feature_vector)
    print "training"
    trainiing(feature_vector, labels, validation_feature_vector, validation_labels)
    # for v in feature_vector:
    #     print v


if __name__ == '__main__':
    main()