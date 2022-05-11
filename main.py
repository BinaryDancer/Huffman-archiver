from huffman import Archiver

import argparse
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compression util.")
    parser.add_argument("-c", "--compress", type=str, help="Path to file to compress")
    parser.add_argument("-d", "--decompress", type=str, help="Path to file to compress")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()
    if args.compress and args.decompress:
        print(
            "\n\u001b[1;31mERROR: Only one mode should be active [--compress, --decompress]!\u001b[0m\n",
            file=sys.stderr,
        )
        exit(1)

    if args.compress:
        arc = Archiver()
        arc.compress(args.compress, args.verbose)

    if args.decompress:
        if args.decompress.split(".")[-1] != "zmh":
            print(
                "\n\u001b[1;31mERROR: Incorrect file fromat to decompress!\u001b[0m\n",
                file=sys.stderr,
            )
            exit(1)
        arc = Archiver()
        arc.decompress(args.decompress, args.verbose)
