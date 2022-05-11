import os
import shutil

if __name__ == "__main__":
    test_dir = "./tests"
    files = os.listdir(test_dir)
    print("DIR FILES:", *files, sep="\n")
    for file in files:
        print("CURR FILE:", file)
        if file.endswith(".zmh"):
            continue
        shutil.make_archive(test_dir + "/" + file, "tar", test_dir)
        shutil.make_archive(test_dir + "/" + file, "zip", test_dir)
