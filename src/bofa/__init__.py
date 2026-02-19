import importlib.metadata

__version__ = importlib.metadata.version("bofa")

BOFA = b'\x42\x6f\x66\x61\x20\x64\x65\x65\x7a\x20\x6e\x75\x74\x73'


def main():
    print(BOFA.decode('utf-8'))
