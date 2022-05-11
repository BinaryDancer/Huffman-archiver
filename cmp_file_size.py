import os


def get_sizes(path):
    zip_path = path + ".zip"
    rar_path = ".".join(path.split(".")[:-1]) + ".rar"
    zmh_path = ".".join(path.split(".")[:-1]) + ".zmh"
    tar_path = path + ".tar"
    return [os.path.getsize(p) for p in [path, rar_path, zip_path, zmh_path, tar_path]]


if __name__ == "__main__":
    test_dir = "./tests"
    files = [
        file
        for file in os.listdir(test_dir)
        if not file.endswith("rar")
        and not file.endswith("zmh")
        and len(file.split(".")) == 2
        and not file.startswith(".")
    ]

    print("{:^30}\t{:>10}\t{:>10}\t{:>10}\t{:>10}\t{:>10}".format("File name", "ORIG", "RAR", "ZIP", "ZMH", "TAR"))
    for file in files:
        res = get_sizes("{}/{}".format(test_dir, file))
        print("{:^30}\t{:>10}\t{:>10}\t{:>10}\t{:>10}\t{:>10}".format(file, *res))
