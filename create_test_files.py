from pathlib import Path

chars = '0123456789'

target_folder = Path('test-files')

target_folder.mkdir(parents=True, exist_ok=True)

for cl in [3, 5, 7, 10]:
    for i in range(7, 9):
        text = chars[:cl] * 10 ** i
        char_prefixes = ["cr", "lf", "crlf", "lfcr", "na"]
        charaters     = ["\r", "\n", "\r\n", "\n\r", ""]
        for char, prefix in zip(charaters, char_prefixes):
            with open(target_folder / f'{prefix}_{cl}chars_{i}.txt', 'w') as w:
                w.write(f"{char}{text}")
