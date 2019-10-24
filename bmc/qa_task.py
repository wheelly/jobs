#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

python3 qa_task.py Error Warn -f ~/test_logs > report.html

Please write python script that receives arguments (array of strings to search, folder
name), and then performs the following:
 Scan the &lt;folder name&gt; (the folder should contain log\s file\s)
 Search for each of the array strings in each of the files
 The outcome should be a report with the below table:
 File Name String Count (number of instances)
A.log Error 2
A.log Fatal 3
B.log Error 1
 Please note:
 Prefer an html report that allows the file name to be a link to the actual file
 The table should be sorted by Count column 
Optional:
The script can also receive an “exclude array list”; On this case, if the detected string exists in
the “array of string to search” but also exists in the “exclude array list” it will not be counted.
"""

import argparse
from os import walk, path
from jinja2 import Template, Environment, FileSystemLoader

def main():
    parser = argparse.ArgumentParser(description='Log level finder (bmc test task)')
    parser.add_argument('-f', '--folder', required=True, help="Folder name. The folder should contain log(s) file(s)")
    parser.add_argument('strings', nargs='+', help='words to count in files')
    parser.add_argument('-e', '--exclude', nargs='+', default=[], help='Exclude string array (not be counted)')
    parser.add_argument('-a', '--asc', action='store_true', default=False)
    parser.add_argument('-t', '--template-path', help="Path to jinja2 template dir", default='./qa_task_tmpl')
    parser.add_argument('--template-file', help="Path to jinja2 template file", default='table.j2')

    args = parser.parse_args()
    try:
        render(args, run(args))
    except Exception as e:
        print(str(e))
        exit(1)


def run(args):

    tokens = set(args.strings) - set(args.exclude)

    def read_file(filename):
        ret = {}
        with open(filename) as f:
            for line in f:
                first_wrd = line.split(sep=None, maxsplit=1)[0]
                if first_wrd in tokens:
                    ret[first_wrd] = ret.get(first_wrd, 0) + 1
        return ret

    out = []
    for root, _, files in walk(args.folder, followlinks=True):
        for file in filter(lambda f: f.endswith('.log'), files):
            stats = read_file(path.join(root, file))
            if stats:
                out.append((root, file, stats))

    out.sort(key=lambda e: list(e[2].values())[0], reverse=not args.asc)
    return out


def render(args, table):
    env = Environment(trim_blocks=True, lstrip_blocks=True,
                      loader=FileSystemLoader(args.template_path))
    template = env.get_template(args.template_file)
    env.globals.update({'table': table})
    print(template.render())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        exit(1)
