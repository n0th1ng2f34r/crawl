# search for valid v2 onion addresses, given some partial address
from os import system
import requests
import datetime
import argparse

CHARS = 'abcdefghijklmnopqrstuvwxyz234567'
CHARS_FLAG_ERROR_MSG = 'ERROR: you fucked up cunt'

PROXIES = {
  'http': 'socks5h://localhost:9050',
  'https': 'socks5h://localhost:9050'
}
HEADERS = {
  'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
}

def generateLog(seed, num, timeout, template):
  partial = ''
  for i in range(16): 
    char = template[1][i]
    if char == '': partial += '-'
    else: partial += char
  date = str(datetime.date.today())
  time = datetime.datetime.now().strftime("%H%M%S")
  logName = date+'-'+time
  f = open('logs/'+logName+'.txt', 'w')
  f.write('# scan initiated at '+logName+' with parameters:\n(d) timeout: '+str(timeout)+'\n(r) seed: '+str(seed)+'\n(i) targets scanned: '+str(num)+'\n(p) partial address: '+partial+'\n')
  f.close()
  return logName

def appendLog(logName, data):
  f = open('logs/'+logName+'.txt', 'a')
  f.write(data)
  f.close()

def int2basek(n, k):
  tmp = n
  res = []
  while tmp > 1:
    res.append(tmp%k)
    tmp = tmp//k
  res.append(tmp)
  res.reverse()
  return res

def pad(t,k): return ([0]*(k-len(t)))+t

def incrementSeed(seed, seedLen, k):
  if 0 > seedLen-k: 
    return seed
  else:
    result = seed
    result[seedLen-k] = (result[seedLen-k]+1)%32
    if result[seedLen-k] == 0:
      return incrementSeed(result, seedLen, k+1)
    else:
      return result

def setupAddress(partialAddress):
  unknown = []
  address = {i:'' for i in range(16)}
  for char in range(16):
    if partialAddress[char] != '0':
      address[char] = partialAddress[char]
    else:
      unknown.append(char)
  return unknown, address

def buildAddress(N, charsIndices, addressTemplate):
  charsSelection = [CHARS[i] for i in N]
  for i in range(len(charsIndices)): 
    addressTemplate[charsIndices[i]] = charsSelection[i]
  address = 'http://'
  for i in range(16): address += addressTemplate[i]
  return address+'.onion'

def ping(address, timeout):
  session = requests.session()
  try:
    r = session.get(address, proxies=PROXIES, headers=HEADERS, timeout=timeout)
  except Exception as e:
    return
  else: 
    return r

def getTitle(reqText):
  regex = "<title.*?>(.+?)</title>"
  pattern = re.compile(regex, re.IGNORECASE)
  try:
      title = re.findall(pattern,reqText)[0]
  except IndexError:
      title = ""
  return title

def scan(seed, num, timeout, template):
  validCount = 0
  logName = generateLog(seed, num, timeout, template)
  print '\n# '+logName+'\n# initiating scan with seed value: '+str(seed)+'\n'
  numScanned = 0
  seedLen = len(template[0])
  addressSeed = pad(int2basek(seed,32), seedLen)
  while numScanned < num:
    address = buildAddress(addressSeed, template[0], template[1])
    req = ping(address, timeout)
    if req == None:
      print '['+str(seed+numScanned)+'] '+address+': not found'
    else:
      validCount += 1
      status = str(req.status_code)
      html = req.text
      title = getSiteTitle(html)
      statement = '['+str(seed+numScanned)+'] '+address+': up with status <'+status+'> and title "'+title+'"'
      appendLog(logName, statement)
      print statement
    addressSeed = incrementSeed(addressSeed, seedLen-1, 0)
    numScanned += 1
  exitTime = str(datetime.date.today())+'-'+datetime.datetime.now().strftime("%H%M%S")
  exitStatement = '\n# scan completed at: '+exitTime+'\n# ['+str(validCount)+'] valid addresses were found during the scan.\n'
  print exitStatement
  appendLog(logName, exitStatement)

def getArgs():
  parser = argparse.ArgumentParser(description='Finds active v2 onion addresses, given a selection of known chars')
  parser.add_argument('-d', '--timeout', help='Sets request timeout', type=int)
  parser.add_argument('-r', '--seed', help='Specifies the starting address seed', type=int)
  parser.add_argument('-i', '--num', help='Specifies the number of addresses to scan', type=int)
  parser.add_argument('-p', '--chars', help='Specifies the known chars', type=str)
  args = parser.parse_args()
  return args

# example usage:
# python crawl.py -d 1 -r 2 -i 3 -p drips0re004mj000
if __name__ == '__main__':
  try:
    args = getArgs()
    if (type(args.chars) == str):

      timeout = 3
      if (type(args.timeout) == int) and (args.timeout > 0): timeout = args.timeout

      seed = 0
      if (type(args.seed) == int) and args.seed > -1: seed = args.seed

      num = 1
      if (type(args.num) == int) and (num > 0): num = args.num

      properlyFormatted = True
      for char in args.chars:
        if char != '0':
          test = CHARS.find(char)
          if (test == -1):
            properlyFormatted = False
      if properlyFormatted:
        if (len(args.chars) == 16):
          template = setupAddress(args.chars)
          if seed > 32**len(template[0]): print CHARS_FLAG_ERROR_MSG
          else: 
            scan(seed, num, timeout, template)
        else:
          print '[0] '+CHARS_FLAG_ERROR_MSG
      else:
        print '[1] '+CHARS_FLAG_ERROR_MSG
    else:
      print '[2] '+CHARS_FLAG_ERROR_MSG

  except KeyboardInterrupt:
    print 'Interrupted by user'
    system.exit(0)
