from subprocess import call
import os
def main():
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
        	s = s.replace("/ORGANIZATION", replacement)
        	s = s.replace("/PERSON", replacement)
        	s = s.replace("/O", replacement)
        	s = s.replace("/LOCATION", "</LOCATION>")
        	with open(fname, "w") as f:
            		f.write(s)
		

main()
