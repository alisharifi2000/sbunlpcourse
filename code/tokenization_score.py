import csv
import os

mapping = {
    'A0': 'A',
    'A1': 'A',
    'A2': 'A',
    'Ab': 'A',
    'Ad': 'A',
    'Al': 'A',
    'C0': 'C',
    'C1': 'C',
    'EXP': 'Exp',
    'INTJ': 'Intj',
    'N1': 'N',
    'N2': 'N',
    'N3': 'N',
    'N4': 'N',
    'N5': 'N',
    'N6': 'N',
    'N7': 'N',
    'N8': 'N',
    'N9': 'N',
    'NA': 'N',
    'NO': 'No',
    'NU': 'No',
    'PO': 'P',
    'PR': 'P',
    'PR1': 'P',
    'SI': 'S',
    'SP': 'S',
    'V1': 'V',
    'V2': 'V',
    'V3': 'V',
    'V4': 'V',
    'V5': 'V',
    'V6': 'V',
    'VPR': 'VPr',
    'PL': 'Pl',
    'Y': 'Y',
    'NEG': 'Neg',
    'O': 'O'
}


def read_conll_file(address):
    ret = []
    line_number = 0
    print('Opening file ', address)
    with open(address, encoding='UTF-8') as f:
        try:
            line = f.readline()
            while line:
                l = line.strip()
                if len(l) == 0:
                    ret.append([])  # End of sentence
                elif line:
                    item = line.split('\t')
                    if len(item) > 6:
                        # print('Warning Line [ ', line_number, '] has  ', len(item), ' tokens it must be 6')
                        item = item[0:7]
                    elif len(item) < 6:
                        # print('Warning Line [ ', line_number, '] has  ', len(item), ' tokens it must be 6')
                        item[len(item):6] = '_' * (6 - len(item))
                    stripped = []
                    for it in item:
                        s = it.strip()
                        if len(s) == 0:
                            s = '_'
                        stripped.append(s)
                    ret.append(stripped)
                line = f.readline()
                line_number += 1
        except:
            print(f'Error Parsing the file: {address}')

    return ret

#
# def longest_common_subsequence_length(s1, s2):
#     m = len(s1)
#     n = len(s2)
#     c = [[0] * (n + 1) for i in range(m + 1)]
#     for i in range(1, m):
#         c[i][0] = 0
#     for j in range(1, n):
#         c[0][j] = 0
#     for i in range(1, m + 1):
#         for j in range(1, n + 1):
#             if s1[i - 1] == s2[j - 1] and s1[i - 1] != '_':  # As _ is equal to empty we will not match them!
#                 c[i][j] = c[i - 1][j - 1] + 1
#             else:
#                 c[i][j] = max(c[i][j - 1], c[i - 1][j])
#     return c[m][n]


def normal_string_matcher(s1 , s2):
    if s1 == s2 and s1 != '_':  # As _ is equal to empty we will not match them!
        return 1
    else:
        return 0


def set_matcher(s1 , s2):
    if s2 == '_' or s1 == '_':  # As _ is equal to empty we will not match them!
        return 0
    return len(set(s1.replace('#' , '|').replace(' ' , '').split('|'))\
        .intersection(set(s2.replace('#' , '|').replace(' ' , '').split('|'))))
def morph_matcher(s1 , s2):

    if len(s1) < 2 or len(s2) < 2 or  s1[0] == '_' or s2[0] == '_' or s1[1] == '_' or s2[1] == '_':
        return 0
    return len(build_morph_set(s1[0] , s1[1]).intersection(build_morph_set(s2[0], s2[1])))


def build_morph_set(struct, analyis):
    struct_parts = struct.replace(' ', '').split('|')
    analyis_parts = analyis.replace(' ', '').lower().split('|')
    ret = set()

    for i in range(min(len(struct_parts), len(analyis_parts))):
        ret.add(struct_parts[i] + analyis_parts[i])
        ret.add(struct_parts[i] + reduced_tag(analyis_parts[i]))
    return ret


def reduced_tag(s):
    ret = []
    parts = s.upper().replace(' ', '').split('+')
    for p in parts:
        if p in mapping:
            ret.append(mapping[p])
        else:
            ret.append('O')
    return '+'.join(ret)

def longest_common_subsequence_general(s1, s2, matcher):
    m = len(s1)
    n = len(s2)
    c = [[0] * (n + 1) for i in range(m + 1)]
    for i in range(1, m):
        c[i][0] = 0
    for j in range(1, n):
        c[0][j] = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            c[i][j] = max(c[i][j - 1], c[i - 1][j], c[i - 1][j - 1] + matcher(s1[i - 1], s2[j - 1]))
    return c[m][n]


def compare_term(ref_items, out_items, ind):  # ind 1:normalized token, 2:stem, 3:lemma
    ref_item = reduce_column(ref_items, ind)
    out_item = reduce_column(out_items, ind)
    count = longest_common_subsequence_general(ref_item, out_item, normal_string_matcher)

    return count


def extract_segment_part(items):
    ret = []
    for ind, r in enumerate(items):
        if len(r) == 0 and ind > 0 and \
                ind < (len(items) - 1) and \
                len(items[ind + 1]) >= 2 and len(items[ind - 1]) >= 2:
            ret.append(items[ind - 1][1] + '_' + items[ind + 1][1])
    return ret


def compare_segment(ref_items, out_items):
    ref_seg = extract_segment_part(ref_items)
    out_seg = extract_segment_part(out_items)

    return longest_common_subsequence_general(ref_seg, out_seg, normal_string_matcher)


def extract_scores():
    path = '../data'
    files = os.scandir(path)
    references = []
    for f in files:
        if f.is_dir():
            print('Processing Folder : ', f.name)
            if os.path.isfile(path + '/' + f.name + '/' + f.name + '.ref'):
                references.append(f.name)
            else:
                print('Warning folder ' + f.name + ' Missing Reference file')

    all_results = []
    for f in os.scandir(path):
        if f.is_dir():
            output_files = os.listdir(path + '/' + f.name + '/')
            for of in output_files:
                if of.endswith('.out'):
                    other_folder = of[:-4]
                    if other_folder in references:
                        print('Evaluating Team ' + f.name + ' Output on Team ' + other_folder + ' Data')
                        scores = score_file(path + '/' + f.name + '/' + of,
                                            path + '/' + other_folder + '/' + other_folder + '.ref')
                        all_results.append([f.name, other_folder] + scores)

    with open('../scores/tokenization.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ['Team', 'Reference Team', 'Total Tokens', 'Segment Score', 'Token Score', 'Stem Score', 'Lemma Score',
             'Morph Score' , 'Morph Analysis Score'])
        for r in all_results:
            writer.writerow(r)


def reduce_column(lst, column):
    ret = []
    if isinstance(column, list):
        ret = [[] for x in range(len(lst))]
        for c in column:
            xx = reduce_column(lst, c)
            for i , v in enumerate(xx):
                ret[i].append(v)
    else:
        for l in lst:
            if len(l) == 0:
                continue
            if column < len(l):
                ret.append(l[column])
            else:
                ret.append('_')
    return ret


def score_file(output_file, ref_file):
    ref_items = read_conll_file(ref_file)
    out_items = read_conll_file(output_file)
    segment_score = compare_segment(ref_items, out_items)
    token_score = compare_term(ref_items, out_items, 1)
    stem_score = compare_term(ref_items, out_items, 2)
    lemma_score = compare_term(ref_items, out_items, 3)
    morph_score = longest_common_subsequence_general(reduce_column(ref_items , 4),
                                                     reduce_column(out_items , 4),
                                                     set_matcher)
    morph_analysis_score = longest_common_subsequence_general(reduce_column(ref_items , [4, 5]),
                                                     reduce_column(out_items , [4, 5]),
                                                     morph_matcher)
    print('Segment Score', segment_score, 'Token score:', token_score, ' Stem Score: ', stem_score, ' Lemma Score: ',
          lemma_score, ' Morph Score: ' ,  morph_score, ' Analysis Score: ' , morph_analysis_score)
    return [len(ref_items), segment_score, token_score, stem_score, lemma_score , morph_score, morph_analysis_score]


def main():
    print('Scoring tool for SBU NLP Project')
    #score_file('../data/sample/sample.out', '../data/sample/sample.ref')
    extract_scores()


if __name__ == "__main__":
    main()
