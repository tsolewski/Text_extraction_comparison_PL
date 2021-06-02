"""
Compare extraction results with other libraries of the same kind.
"""

# import logging
import os
import re
import time

from lxml import etree, html
from lxml.html.clean import Cleaner
#HTML_CLEANER = Cleaner()

try:
    import cchardet as chardet
except ImportError:
    import chardet

import html2text
import html_text
import justext
#from boilerpy3 import extractors
#from dragnet import extract_content #, extract_content_and_comments
from goose3 import Goose
#from inscriptis import get_text
#from jparser import PageModel
# from libextract.api import extract as lib_extract
from newspaper import fulltext
#from newsplease import NewsPlease
from readabilipy import simple_json_from_html_string
from readability import Document
from trafilatura import extract

## TODO: time, best of 3

from evaldata_news import EVAL_PAGES
try:
    from trafilatura.core import baseline
except ImportError:
    baseline = None
from trafilatura.utils import sanitize

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

TEST_DIR = os.path.abspath(os.path.dirname(__file__))

#boilerpipe_extractor = extractors.ArticleExtractor()  # ArticleExtractor DefaultExtractor LargestContentExtractor

g = Goose()


def trim(string):
    '''Remove unnecessary spaces within a text string'''
    if string is not None:
        # delete newlines that are not related to punctuation or markup
        # string = re.sub(r'(?<![p{P}>])\n', ' ', string)
        # proper trimming
        string = ' '.join(re.split(r'\s+', string.strip(' \t\n\r'), flags=re.UNICODE|re.MULTILINE))
        string = string.strip()
    return string


def load_document_binary(filename):
    '''load mock page from samples'''
    mypath = os.path.join(TEST_DIR, 'cache', filename)
    if not os.path.isfile(mypath):
        mypath = os.path.join(TEST_DIR, 'eval', filename)
    #if not os.path.isfile(mypath):
    #    mypath = os.path.join(TEST_DIR, 'additional', filename)
    with open(mypath, 'rb') as inputf:
        htmlstring = inputf.read()
    return htmlstring


def load_document_string(filename):
    '''load mock page from samples'''
    mypath = os.path.join(TEST_DIR, 'cache', filename)
    if not os.path.isfile(mypath):
        mypath = os.path.join(TEST_DIR, 'eval', filename)
    #if not os.path.isfile(mypath):
    #    mypath = os.path.join(TEST_DIR, 'additional', filename)
    try:
        with open(mypath, 'r') as inputf:
            htmlstring = inputf.read()
    # encoding/windows fix for the tests
    except UnicodeDecodeError:
        # read as binary
        with open(mypath, 'rb') as inputf:
            htmlbinary = inputf.read()
        guessed_encoding = chardet.detect(htmlbinary)['encoding']
        if guessed_encoding is not None:
            try:
                htmlstring = htmlbinary.decode(guessed_encoding)
            except UnicodeDecodeError:
                htmlstring = htmlbinary
        else:
            print('Encoding error')
    return htmlstring


def run_baseline_2(htmlstring):
    '''run bare text extraction within lxml'''
    # binary/string as input tweak
    try:
        tree = html.fromstring(htmlstring)
    except ValueError:
        tree = html.fromstring(htmlstring.encode('utf8'))
    result = None
    # try json-ld
    for elem in tree.xpath('//script[@type="application/ld+json"]'):
        if elem.text and '"articleBody":' in elem.text:
            mymatch = re.search(r'"articleBody":"(.+?)","', elem.text)
            if mymatch:
                result = mymatch.group(1)
                result = result.replace('\\"', '"')
                # result = trim(result)
                break
    if result is not None:
        return result
    #results = set()
    resultlist = list()
    # iterate potentially relevant elements
    for element in tree.iter('blockquote', 'code', 'p', 'pre', 'q'): # 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
        #if element.tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        #    if not element.text or len(element.text) < 20:
        #        continue
        #    entry = element.text
        #else:
        entry = element.text_content()
        #if entry not in results and len(entry) > 10:
        resultlist.append(entry)
        #results.add(entry)
    # if nothing has been found
    #if len(resultlist) < 1:
    #    for element in tree.iter('b', 'em', 'i', 'strong'):
    #        entry = element.text_content()
    #        #if entry not in results: # and len(entry) > 15:
    #        resultlist.append(entry)
    #        #results.add(entry)
    #if len(resultlist) == 0:
    #    cleaned_tree = HTML_CLEANER.clean_html(tree)
    #    for element in tree.iter('div'):
    #        entry = element.text_content()
            #if len(entry) > 15:
    #        resultlist.append(entry)
    #        #results.add(entry)
    #print(len(resultlist))
    result = '\n'.join(resultlist)
    # result = sanitize(result)
    # print(result)
    return result


def run_baseline(htmlstring):
    '''run bare text extraction within lxml'''
    if baseline is not None:
        _, result, _ = baseline(htmlstring)
        return result
    result = run_baseline_2(htmlstring)
    return result


def run_trafilatura(htmlstring):
    '''run trafilatura (without fallback) on content'''
    result = extract(htmlstring, no_fallback=True, include_comments=False, include_tables=True, include_formatting=False, target_language='pl')
    return result


def run_justext(htmlstring):
    '''try with the generic algorithm justext'''
    valid = list()
    paragraphs = justext.justext(htmlstring, justext.get_stoplist("Polish"), 50, 200, 0.1, 0.2, 0.2, 200, True)  # stop_words
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            valid.append(paragraph.text)
    result = ' '.join(valid)
    return result # sanitize(result)


def run_trafilatura_fallback(htmlstring):
    '''run trafilatura (with fallback) on content'''
    result = extract(htmlstring, no_fallback=False, include_comments=False, include_tables=True, include_formatting=False, target_language='pl')
    return result


def run_goose(htmlstring):
    '''try with the goose algorithm'''
    try:
        article = g.extract(raw_html=htmlstring)
        return article.cleaned_text # sanitize(article.cleaned_text)
    except ValueError:
        return ''


def run_readability(htmlstring):
    '''try with the Python3 port of readability.js'''
    try:
        doc = Document(htmlstring)
        return doc.summary() # sanitize(doc.summary())
    except Exception as err:
        print('Exception:', err)
        return ''

def run_html2text(htmlstring):
    '''try with the html2text module'''
    try:
        text = html2text.html2text(htmlstring)
        # sanitize(text)
    except TypeError:
        text = ''
    return text


def run_html_text(htmlstring):
    '''try with the html2text module'''
    try:
        text = html_text.extract_text(htmlstring, guess_layout=False)
    except TypeError:
        text = ''
    return text


def run_newspaper(htmlstring):
    '''try with the newspaper module'''
    try:
        text = fulltext(htmlstring) # sanitize(fulltext(htmlstring))
    except AttributeError:
        return ''
    return text

def evaluate_result(result, item):
    '''evaluate result contents'''
    true_positives = 0
    false_negatives = 0
    false_positives = 0
    true_negatives = 0
    # report if problematic
    if len(item['with']) == 0 or len(item['with']) > 6:
        print('counter', item)
    if len(item['without']) == 0 or len(item['without']) > 6:
        print('counter', item)
    # internal report
    #if result is None:
    #    print('None', item['file'])
    #elif type(result) is not str:
    #    print('not str', item['file'])
    # examine
    if result is not None and type(result) is str:
        # expected output
        for to_include in item['with']:
            if to_include in result:
                true_positives += 1
            else:
                false_negatives += 1
        # unwanted output
        for to_exclude in item['without']:
            if to_exclude in result:
                false_positives += 1
            else:
                true_negatives += 1
    # add up as bulk counts
    else:
        false_negatives += len(item['with'])
        true_negatives += len(item['without'])
    return true_positives, false_negatives, false_positives, true_negatives


def calculate_scores(mydict):
    '''output weighted result score'''
    tp, fn, fp, tn = mydict['true positives'], mydict['false negatives'], mydict['false positives'], mydict['true negatives']
    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    accuracy = (tp+tn)/(tp+tn+fp+fn)
    fscore = (2*tp)/(2*tp + fp + fn)  # 2*((precision*recall)/(precision+recall))
    return precision, recall, accuracy, fscore


template_dict = {'true positives': 0, 'false positives': 0, 'true negatives': 0, 'false negatives': 0, 'time': 0}
nothing, everything, baseline_result, trafilatura_result, justext_result, trafilatura_fallback_result, goose_result, readability_result, inscriptis_result, newspaper_result, html2text_result, html_text_result, dragnet_result, boilerpipe_result, newsplease_result, jparser_result, readabilipy_result = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
nothing.update(template_dict)
everything.update(template_dict)
baseline_result.update(template_dict)
trafilatura_result.update(template_dict)
justext_result.update(template_dict)
trafilatura_fallback_result.update(template_dict)
goose_result.update(template_dict)
readability_result.update(template_dict)
inscriptis_result.update(template_dict)
newspaper_result.update(template_dict)
html2text_result.update(template_dict)
html_text_result.update(template_dict)
dragnet_result.update(template_dict)
boilerpipe_result.update(template_dict)
newsplease_result.update(template_dict)
jparser_result.update(template_dict)
readabilipy_result.update(template_dict)


i = 0

for item in EVAL_PAGES:
    if len(EVAL_PAGES[item]['file']) == 0:
        continue
    # print(EVAL_PAGES[item]['file'])
    htmlstring = load_document_string(EVAL_PAGES[item]['file'])
    if htmlstring is None:
        continue
    # print(type(htmlstring))
    # null hypotheses
    tp, fn, fp, tn = evaluate_result('', EVAL_PAGES[item])
    nothing['true positives'] += tp
    nothing['false positives'] += fp
    nothing['true negatives'] += tn
    nothing['false negatives'] += fn
    tp, fn, fp, tn = evaluate_result(htmlstring, EVAL_PAGES[item])
    everything['true positives'] += tp
    everything['false positives'] += fp
    everything['true negatives'] += tn
    everything['false negatives'] += fn
    # html2text
    start = time.time()
    result = run_html2text(htmlstring)
    html2text_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    html2text_result['true positives'] += tp
    html2text_result['false positives'] += fp
    html2text_result['true negatives'] += tn
    html2text_result['false negatives'] += fn
    # html_text
    start = time.time()
    result = run_html_text(htmlstring)
    html_text_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    html_text_result['true positives'] += tp
    html_text_result['false positives'] += fp
    html_text_result['true negatives'] += tn
    html_text_result['false negatives'] += fn
    # inscriptis
    start = time.time()
    # result = run_inscriptis(htmlstring)
    inscriptis_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    inscriptis_result['true positives'] += tp
    inscriptis_result['false positives'] += fp
    inscriptis_result['true negatives'] += tn
    inscriptis_result['false negatives'] += fn
    # bare lxml
    start = time.time()
    result = run_baseline(htmlstring)
    baseline_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    baseline_result['true positives'] += tp
    baseline_result['false positives'] += fp
    baseline_result['true negatives'] += tn
    baseline_result['false negatives'] += fn
    # trafilatura
    start = time.time()
    result = run_trafilatura(htmlstring)
    trafilatura_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    trafilatura_result['true positives'] += tp
    trafilatura_result['false positives'] += fp
    trafilatura_result['true negatives'] += tn
    trafilatura_result['false negatives'] += fn
    # justext
    start = time.time()
    result = run_justext(htmlstring)
    justext_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    justext_result['true positives'] += tp
    justext_result['false positives'] += fp
    justext_result['true negatives'] += tn
    justext_result['false negatives'] += fn
    # trafilatura + X
    start = time.time()
    result = run_trafilatura_fallback(htmlstring)
    trafilatura_fallback_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    trafilatura_fallback_result['true positives'] += tp
    trafilatura_fallback_result['false positives'] += fp
    trafilatura_fallback_result['true negatives'] += tn
    trafilatura_fallback_result['false negatives'] += fn
    # readability
    start = time.time()
    result = run_readability(htmlstring)
    readability_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    readability_result['true positives'] += tp
    readability_result['false positives'] += fp
    readability_result['true negatives'] += tn
    readability_result['false negatives'] += fn
    # goose
    start = time.time()
    result = run_goose(htmlstring)
    goose_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    goose_result['true positives'] += tp
    goose_result['false positives'] += fp
    goose_result['true negatives'] += tn
    goose_result['false negatives'] += fn
    # newspaper
    start = time.time()
    result = run_newspaper(htmlstring)
    newspaper_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    newspaper_result['true positives'] += tp
    newspaper_result['false positives'] += fp
    newspaper_result['true negatives'] += tn
    newspaper_result['false negatives'] += fn
    # dragnet
    start = time.time()
    # result = run_dragnet(htmlstring)
    dragnet_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    dragnet_result['true positives'] += tp
    dragnet_result['false positives'] += fp
    dragnet_result['true negatives'] += tn
    dragnet_result['false negatives'] += fn
    # boilerpipe
    start = time.time()
    # result = run_boilerpipe(htmlstring)
    boilerpipe_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    boilerpipe_result['true positives'] += tp
    boilerpipe_result['false positives'] += fp
    boilerpipe_result['true negatives'] += tn
    boilerpipe_result['false negatives'] += fn
    # newsplease
    start = time.time()
    # result = run_newsplease(htmlstring)
    newsplease_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    newsplease_result['true positives'] += tp
    newsplease_result['false positives'] += fp
    newsplease_result['true negatives'] += tn
    newsplease_result['false negatives'] += fn
    # jparser
    start = time.time()
    # result = run_jparser(htmlstring)
    jparser_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    jparser_result['true positives'] += tp
    jparser_result['false positives'] += fp
    jparser_result['true negatives'] += tn
    jparser_result['false negatives'] += fn
    # readabilipy
    start = time.time()
    # result = run_readabilipy(htmlstring)
    readabilipy_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    readabilipy_result['true positives'] += tp
    readabilipy_result['false positives'] += fp
    readabilipy_result['true negatives'] += tn
    readabilipy_result['false negatives'] += fn
    # counter
    i += 1
    # print(i)


# print('number of documents:', i)

print('baseline')
print(baseline_result)
try:
    print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(baseline_result)))
except ZeroDivisionError:
    pass

print('html2text')
print(html2text_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(html2text_result)))
print("time diff.: %.2f" % (html2text_result['time'] / baseline_result['time']))

print('html_text')
print(html_text_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(html_text_result)))
print("time diff.: %.2f" % (html_text_result['time'] / baseline_result['time']))

print('justext')
print(justext_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(justext_result)))
print("time diff.: %.2f" % (justext_result['time'] / baseline_result['time']))

print('newspaper')
print(newspaper_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(newspaper_result)))
print("time diff.: %.2f" % (newspaper_result['time'] / baseline_result['time']))

print('readability')
print(readability_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(readability_result)))
print("time diff.: %.2f" % (readability_result['time'] / baseline_result['time']))

print('trafilatura')
print(trafilatura_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(trafilatura_result)))
print("time diff.: %.2f" % (trafilatura_result['time'] / baseline_result['time']))

print('trafilatura + X')
print(trafilatura_fallback_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(trafilatura_fallback_result)))
print("time diff.: %.2f" % (trafilatura_fallback_result['time'] / baseline_result['time']))
