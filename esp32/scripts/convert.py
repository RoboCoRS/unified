from sys import argv
import re


def main():
    if len(argv) != 2:
        print('Usage: FILE')
        return

    with open(argv[1], 'r') as f:
        content = f.read()

    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'"', '\\"', content)
    content = content.strip()

    print('#pragma once')
    print()
    print('#include <Arduino.h>')
    print()
    print(f'const String base_html = "{content}";')


if __name__ == '__main__':
    main()
