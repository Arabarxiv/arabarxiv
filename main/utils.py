# utils.py
import re

def format_bibtex_for_arabic(bibtex_input):
    lines = bibtex_input.split('\n')
    formatted_lines = []

    for line in lines:
        if 'author' in line:
            # Replace 'and' with 'و'
            line = line.replace('and', 'و')
            # Remove commas
            line = line.replace(',', '')
            # Double the accolades if present
            if '{' in line and '}' in line:
                line = line.replace('{', '{{').replace('}', '}}')
        elif 'journal' in line:
            # Reverse word order if it contains Latin characters
            if re.search('[a-zA-Z]', line):
                words = line.split()
                line = ' '.join(reversed(words))
        formatted_lines.append(line)

    return '\n'.join(formatted_lines)
