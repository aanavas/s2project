import sys
import codecs
import random

def train_test(ifilename, test_lines):
    ifile = codecs.open(ifilename, 'r', 'utf-8')
    ofilename = '.'.join(ifilename.split('.')[:-1])
    tst_file = codecs.open(ofilename + '.test', 'w', 'utf-8')
    trn_file = codecs.open(ofilename + '.train', 'w', 'utf-8')
    
    lines = ifile.read().split('\n')
    lines = [l.strip() for l in lines if len(l.strip())>0 and '_' not in l]
    random.shuffle(lines)
    
    tst_file.write('\n'.join(lines[:test_lines]))
    trn_file.write('\n'.join(lines[test_lines:]))
    tst_file.close()
    trn_file.close()
    
if __name__ == '__main__':
    lang = sys.argv[1]
    test_size = int(sys.argv[2])
    ifilename = 'data/%s/%s.dic' % (lang, lang)
    
    train_test(ifilename, test_size)
