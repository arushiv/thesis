
# coding: utf-8

import pandas
import numpy
import re
import sys
import argparse

def getOpts():
    parser = argparse.ArgumentParser(description="""Convert citekyes from 'lastname et al year' format to bibtex citekey """)
    parser.add_argument('--txt', help="""input text file with citations in genetics format""")
    parser.add_argument('--ref', help="""input text file with biblipgraphy in genetics format""")
    parser.add_argument('--bib', type=float, help="""latex .bib file""")
    parser.add_argument('--output', help="""output tex filename""")
    args = parser.parse_args()
    return args


def fetch_citekeys(filename):
    """1. get all citation refs <lastname> et al. <year> or
    <name> and <name> <year> from the file to
    match with ref list
    """
    f = open(filename)
    l = []

    for line in f:
        # citekeys with et al
        found = re.findall(" \S+ et al. \d{4}", line)
        if len(found)>0:
            l.append(found)

        # citekeys with 2 authors
        found_2 = re.findall(" \S+ and \S+ \d{4}", line)
        if len(found_2)>0:
            l.append(found_2)

    return l

def flatten_list(l):
    # Flatten list
    final = []

    for s1 in l:
        if type(s1) is list:
            for s2 in s1:
                string = s2.split("(")[-1].replace("]", "").lstrip()
                final.append(string)
        else:
            final.append(s1.lstrip())
        
    final_refs = list(set(final))
    return final_refs

def match_refs(x):
    matches = []
    for ref in final_refs:
        split = ref.split(" ")
        refstart = split[0]
        year = split[-1]
        if x.startswith(refstart) and year in x:
            matches.append(ref)
    if len(matches) == 1:
        year = matches[0].split(' ')[-1]
        title = x.split(f"{year} ")[1].split('.')[0]
        return matches[0], title
    else:
        return numpy.nan, numpy.nan


def replace(line):
    print(line)
    for index, row in matched.iterrows():
        line = line.replace(row['citation'], "\cite{{{c}}}".format(c=row['index']))
    print(line)
    return line


if __name__ == '__main__':
    
    args = getOpts()

    texfile = args.tex
    # Get all citation refs 
    l = fetch_citekeys(texfile)
    final_refs = flatten_list(l)
        
    # Match citations with title refs 
    f = open(args.refs)
    r = f.readlines()
    refs = pandas.DataFrame(r, columns=['ref'])

    
    refs['citation'], refs['title'] = zip(*refs['ref'].map(match_refs))
    refs['low_title'] = refs['title'].str.lower()
    refs.head()

    #get bibliograpgy citekeys
    t = open(args.bib)
    lines = t.readlines()
    bibs = pandas.DataFrame(lines)
    
    df = pandas.DataFrame()

    for index, row in bibs.iterrows():
        if row[0].startswith("@article{") and bibs.iloc[index + 1][0].lstrip().startswith("title"):
            citekey = row[0].replace("@article{", "").replace(",\n", "")
            title = bibs.iloc[index + 1][0].lstrip().replace("title = ", "").replace("{", "").replace("}", "").replace(",", "").replace(".", "").rstrip()
            df.loc[citekey, 'title'] = title
            
    df.reset_index(inplace=True)
    df['low_title'] = df['title'].str.lower()
    df.head()

    matched = pandas.merge(refs, df, how="inner", on="low_title")
    matched.head()

    outfile = open(args.output)

    with open(outfile, 'w+') as f:
        for line in texfile.readlines():
            newline = replace(line)
            f.write(newline)


        
