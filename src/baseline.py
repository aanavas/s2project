import LTS_RuleLearnerSrvr
import codecs
import random
import sys
#import xmlrpclib

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s1:
        return len(s2)
 
    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
 
    return previous_row[-1]

def read_dictionary(ifilename):
    ifile = codecs.open(ifilename, 'r', 'utf-8')
    lines = ifile.read().split('\n')
    data = []
    for line in lines:
        entry = line.strip().split()
        if len(entry) == 0: continue
        data.append((entry[0].lower(), ' '.join(entry[1:])))
    return data

def get_training_data(lang):
    ifilename = 'data/%s/%s.train' % (lang, lang)
    data = read_dictionary(ifilename)
    random.shuffle(data)
    return data

def get_test_data(lang):
    ifilename = 'data/%s/%s.test' % (lang, lang)
    return read_dictionary(ifilename)

def test(svr, lang):
    data = get_test_data(lang)

    total_phones = 0
    correct_phones = 0
    total_words = len(data)
    correct_words = 0    

    for word, phones in data[:total_words]:
        phone_array = phones.split()
        total_phones += len(phone_array)
        
        answer = svr.PredictOneWord(word, 1)
        answer_array = answer.split()
        
        distance = levenshtein(phone_array, answer_array)
        correct_phones += len(phone_array) - distance
        
        if phones == answer:
            correct_words += 1
            
        #print word, ':', phones, ' == ', answer, '?', distance
        
    word_acc = correct_words * 100.0 / total_words
    phone_acc = correct_phones * 100.0 / total_phones
    #print 'Word accuracy:', word_acc
    #print 'Phone accuracy:', phone_acc
    
    return (word_acc, phone_acc)

def baseline(lang, data, sizes):
    #svr = xmlrpclib.Server ('http://localhost:8000', encoding = 'utf-8')
    svr = LTS_RuleLearnerSrvr.T ([], [], unknown_phone_symbol='*')
    
    results = []
    for count, (word, phones) in enumerate(data[:sizes[-1]]):
        #print word, '=', phones
        if count+1 in sizes:
            svr.SubmitPronunciation (word, phones)
            (wa, pa) = test(svr, lang)
            results.append((count+1, wa, pa))
            print count+1, wa, pa
        else:
            svr.SubmitPronunciation (word, phones, stype='incr')
    
    #answer = svr.Get_LTS_Rules()
    #print answer
    
    return results

if __name__ == '__main__':
    lang = sys.argv[1]
    sizes = [int(s) for s in sys.argv[2].split(',')]
    iterations = int(sys.argv[3])
    
    was = dict((size, set()) for size in sizes)
    pas = dict((size, set()) for size in sizes)
    for iteration in range(iterations):
        #print "iteration %s..." % (iteration+1),
        data = get_training_data(lang)
        results = baseline(lang, data, sizes)
        for size, wa, pa in results:
            was[size].add(wa)
            pas[size].add(pa)
        #print 'done!'
        
    avg = lambda x : sum(x)*1.0/len(x)
    for size in sizes:
        print size, avg(was[size]), avg(pas[size])
