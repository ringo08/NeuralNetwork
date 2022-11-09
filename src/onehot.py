import os

if __name__ == '__main__':
  path = 'test_data.txt'

  alpha2num = lambda c: ord(c) - ord('a') + 1
  with open(f'{path}', 'rt', encoding='utf-8') as f:
    strings = f.readlines()
    sLen = len(strings[0].split(' ')[0])
    maxTarget = max([int(s.split(' ')[1]) for s in strings])
  
  with open(f'{path.split(".")[0]}.csv', 'wt', encoding='utf-8') as f:
    print(f'{26*sLen}, {maxTarget}', file=f)
    for words in strings:
      array = []
      word, target = tuple(words.split(' '))
      for s in word:
        if s == '-':
          array.append(','.join(['0']*26))
        else:
          sNum = alpha2num(s)
          array.append(','.join(['1' if i+1==sNum else '0' for i in range(26)]))
      array.extend(['1' if i+1==int(target) else '0' for i in range(maxTarget)])
      print(','.join(array), file=f)
