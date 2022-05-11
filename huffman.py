from collections import defaultdict, deque
from time import time
import queue


class Archiver:
    class Node:
        def __init__(self, value: bytes = None, freq: int = 0) -> None:
            self.freq: int = freq
            self.value: bytes = value
            self.left: Archiver.Node = None
            self.right: Archiver.Node = None

        def __eq__(self, __o: object) -> bool:
            return self.freq == __o.freq

        def __gt__(self, __o: object) -> bool:
            return self.freq > __o.freq

        def __ge__(self, __o: object) -> bool:
            return self.freq >= __o.freq

        def __lt__(self, __o: object) -> bool:
            return self.freq < __o.freq

        def __le__(self, __o: object) -> bool:
            return self.freq <= __o.freq

    def __init__(self) -> None:
        self.bdict = defaultdict(int)

    def compress(self, file_path: str, verbose: bool = False) -> None:
        st_time = time()

        if len(file_path.split("/")[-1].split(".")) == 1:
            output_path = file_path + ".zmh"
        else:
            output_path = ".".join(file_path.split(".")[:-1]) + ".zmh"

        with open(file_path, "rb") as f:
            edata = f.read()

        self._build_dict(edata)
        if len(self.bdict) == 0:
            if len(file_path.split("/")[-1].split(".")) == 1:
                bstr_file_type = ""
            else:
                bstr_file_type = "".join(
                    ["{:0>8}".format(bin(ord(el))[2:]) for el in file_path.split(".")[-1]]
                )
            bstr_out_data = (
                "0" * 9
                + "{:0>8}".format(bin(len(bstr_file_type)//8)[2:])
                + bstr_file_type
            )
            cnt_zeros = 8 - len(bstr_out_data) % 8
            bstr_out_data += "0" * cnt_zeros + "{:0>8}".format(bin(cnt_zeros)[2:])

            if verbose:
                print(
                    "\n\u001b[32mBin output data\u001b[0m\n{}\n".format(bstr_out_data)
                )

            self._write_bdata(bstr_out_data, output_path, verbose)
            print(
                "\n\u001b[32mCompressed:\u001b[0m{:.2f} sec.\n".format(time() - st_time)
            )
            return

        huff_tree: Archiver.Node = self._create_huff_tree(
            [(v, f) for v, f in self.bdict.items()]
        )

        if verbose:
            print(
                "\n\u001b[32mBytes 2 frequency dict:\u001b[0m\n{}\n".format(self.bdict)
            )
            print("\n\u001b[32mHuffman tree\u001b[0m\n")
            self._print_tree(huff_tree)

        mapping_dict = self._get_mapping(huff_tree)

        if verbose:
            print("\n\u001b[32mHuffman mapping:\u001b[0m\n{}\n".format(mapping_dict))

        bstr_encoded_data = "".join([mapping_dict[el] for el in edata])

        bstr_huff_table = ""
        for b, c in sorted(mapping_dict.items(), key=lambda x: len(x[1])):
            c_len = "{:0>9}".format(bin(len(c))[2:])
            bstr_huff_table += c_len + c + "{:0>8}".format(bin(b)[2:])

        if len(file_path.split("/")[-1].split(".")) == 1:
            bstr_file_type = ""
        else:
            bstr_file_type = "".join(
                ["{:0>8}".format(bin(ord(el))[2:]) for el in file_path.split(".")[-1]]
            )
        bstr_out_data = (
            bstr_huff_table
            + "0" * 9
            + "{:0>8}".format(bin(len(bstr_file_type)//8)[2:])
            + bstr_file_type
            + bstr_encoded_data
        )
        cnt_zeros = 8 - len(bstr_out_data) % 8
        bstr_out_data += "0" * cnt_zeros + "{:0>8}".format(bin(cnt_zeros)[2:])

        if verbose:
            print("\n\u001b[32mHuffman table\u001b[0m\n{}\n".format(bstr_huff_table))
            print("\n\u001b[32mBin output data\u001b[0m\n{}\n".format(bstr_out_data))

        self._write_bdata(bstr_out_data, output_path, verbose)

        print("\n\u001b[32mCompressed:\u001b[0m {:.2f} sec.\n".format(time() - st_time))

    def decompress(self, file_path: str, verbose: bool = False) -> None:
        st_time = time()

        with open(file_path, "rb") as f:
            edata = f.read()

        bdata = self._to_bits(edata)

        if verbose:
            print("\n\u001b[32mEncoded input\u001b[0m\n{}\n".format(edata))
            print("\n\u001b[32mBits input\u001b[0m\n{}\n".format(bdata))

        file_type, bstr_out_data = self._parse_bdata(bdata, verbose)
        output_path = ".".join(file_path.split(".")[:-1]) + ("." + file_type if len(file_type) > 0 else "")

        self._write_bdata(bstr_out_data, output_path, verbose)

        print(
            "\n\u001b[32mDecompressed:\u001b[0m {:.2f} sec.\n".format(time() - st_time)
        )

    def _build_dict(self, bdata: bytes) -> None:
        for i in bdata:
            self.bdict[i] += 1

    def _create_huff_tree(self, elements: list) -> Node:
        nodes_list = [Archiver.Node(v, f) for v, f in elements]
        while len(nodes_list) > 1:
            nodes_list.sort(reverse=True)

            lnode, gnode = nodes_list.pop(), nodes_list.pop()
            new_node = Archiver.Node(freq=lnode.freq + gnode.freq)
            new_node.left = lnode
            new_node.right = gnode

            nodes_list.append(new_node)
        return nodes_list[0]

    def _get_mapping(self, tree: Node) -> dict:
        byte2code = {}
        curr_code = ""

        def get_code(node: Archiver.Node):
            nonlocal curr_code
            if node.left:
                curr_code += "0"
                get_code(node.left)
            if node.right:
                curr_code += "1"
                get_code(node.right)
            if node.value is not None:
                byte2code[node.value] = curr_code[:]
            curr_code = curr_code[:-1]

        get_code(tree)
        if len(byte2code.keys()) == 1:
            byte2code[list(byte2code.keys())[0]] = "1"
        return byte2code

    def _print_tree(self, tree: Node) -> dict:
        l: deque[Archiver.Node] = deque()
        l.append([tree])
        cnt = 0
        while len(l) > 0:
            print("Level:", cnt)
            next_level = []
            curr_level = l.pop()
            for n in curr_level:
                print("\t", n.freq, n.value)
                if n.left:
                    next_level.append(n.left)
                if n.right:
                    next_level.append(n.right)
            if next_level:
                l.append(next_level)
            cnt += 1
            print()

    def _write_bdata(self, bdata: str, output_path: str, verbose: bool = False) -> None:
        encoded_output = bytearray(
            int(bdata[i : i + 8], 2) for i in range(0, len(bdata), 8)
        )

        if verbose:
            print("\n\u001b[32mOutput file:\u001b[0m\n{}\n".format(output_path))
            print("\n\u001b[32mEncoded output\u001b[0m\n{}\n".format(encoded_output))

        with open(output_path, "wb") as f:
            f.write(bytes(encoded_output))

    def _parse_bdata(self, bdata: str, verbose: bool = False) -> tuple:
        i = 0
        mapping_dict = {}

        while i < len(bdata):
            code_len = int(bdata[i : i + 9], 2)
            i += 9
            if code_len == 0:
                break
            mapping_dict[bdata[i : i + code_len]] = bdata[
                i + code_len : i + code_len + 8
            ]
            i += code_len + 8

        file_type_len = int(bdata[i : i + 8], 2)
        i += 8

        file_type = ""
        for j in range(file_type_len):
            file_type += chr(int(bdata[i + j * 8 : i + j * 8 + 8], 2))

        if verbose:
            print("\n\u001b[32mHuffman mapping:\u001b[0m\n{}\n".format(mapping_dict))
            print("\n\u001b[32mOutput file type:\u001b[0m\n{}\n".format(file_type))

        cnt_extra_zeros = int(bdata[-8:], 2)
        compressed_bdata = bdata[i + file_type_len * 8 : -cnt_extra_zeros - 8]
        bstr_out_data = self._decompress(compressed_bdata, mapping_dict)

        if verbose:
            print("\n\u001b[32mBin output data\u001b[0m\n{}\n".format(bstr_out_data))

        return file_type, bstr_out_data

    def _decompress(self, bdata: str, mapping_dict: dict) -> str:
        i = 0
        output = ""
        while i < len(bdata):
            code = ""
            while mapping_dict.get(code) is None:
                code += bdata[i]
                i += 1
            output += mapping_dict[code]

        return output

    def _to_bits(self, encoded_data: bytes) -> str:
        return "".join(["{:0>8}".format(bin(x)[2:]) for x in encoded_data])
