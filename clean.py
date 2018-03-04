import os

files = os.listdir("./mod/")

for fname in files:
    if not fname.endswith(".txt"):
        continue

    with open("./mod/" + fname) as f:
        print fname
        s = f.read()

    lines = s.replace("``", '"')

    with open("./mod_clean/" + fname, 'w') as the_file:
        the_file.write(lines)
