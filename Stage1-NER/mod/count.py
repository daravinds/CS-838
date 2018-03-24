from subprocess import call
import os
def main():
	count = {}
        files = os.listdir("./")
        #f = []
        for fname in files:
                if not fname.endswith(".txt"):
                        continue
                print fname

                replacement = ""
                fpath = os.path.join("./", fname)
                with open(fname) as f:
                        s = f.read()
		words = s.split(" ")
		for word in words:
			if "#LOCATION" in word:
				word = word.replace("#LOCATION","")
				c = count.get(word,0)
				count[word] = c + 1
	print count
	total = 0
	for word in count:
		total += count[word]
	print total
main()
