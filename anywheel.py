token = ''

cache = {
    'user1': 'token1',
    'user2': 'token2',
}

########## CODE ##########
import requests,json,sys,time,re

functions = ['p','c','s','d','o','l','g','h','u','n']

def usage(): 
  usage = '''usage:
anywheel g mobiles*\t\tsubmit OTP for token generation
anywheel u [tokens*|all]\tsee user data
anywheel p [tokens*|all]\tsee current point total
anywheel c [tokens*|all]\tcheck in
anywheel s [tokens*|all]\tshare trip
anywheel d [tokens*|all]\tcheck in and share trip
anywheel h [tokens*|all]\tview last 10 trips
anywheel o [tokens*|all]\tbuy one day pass
anywheel # [tokens*|all]\tbuy seven day pass # times
anywheel n [tokens*|all]\tbuy $1 coupon
anywheel l [token] tripids*\tlookup trip data
  '''
  print(usage)
  quit()

### input validation ###
if len(sys.argv) < 2 or (len(sys.argv) == 2 and not token) or (len(sys.argv) <= 3 and sys.argv[1] == 'l' and not token): usage()
elif sys.argv[1] not in functions: 
    try: assert int(sys.argv[1]) >= 0
    except: usage()
elif sys.argv[1] in ['l','g']:
    for n in sys.argv[3 if sys.argv[1]=='l' and len(sys.argv) > 3 else 2:]:
        try: assert int(n) >= 0
        except: usage()
      
### POST headers ###
h = {
    'X-Atayun-Os-Version':'15.5',
    'X-Atayun-Os':'0',
    'Content-Type':'application/json',
    'Authorization':'Basic YW55d2hlZWw6TXNId3lPMDB5S0RhMzlCeU0=',
    'X-Atayun-Version':'2.3.7',
    'X-Atayun-Api-Version':'10',
    'Accept':'*/*',
    'X-Atayun-Network':'0',
    'Accept-Language':'en-SG;q=1',
    'Accept-Encoding':'gzip, deflate',
    'X-Atayun-Screen':'750x1334',
    'X-Atayun-Brand':'iPhone SE (2nd generation)',
    'User-Agent':'Anywheel/2.3.7 (iPhone; iOS 15.5; Scale/2.00)',
    'X-Atayun-Versioncode':'354'
}

### token generation ###
# request OTP
def request(m):
    r = json.loads(requests.post('https://appgw.justscoot.com/noAuth/login/captcha','{"type":1,"cc":"65","mobile":"%s"}'%m,headers=h).text)
    if r['msg'] == 'Your verification code has been sent.': 
        print('OTP sent to %s'%m)
        return True
    elif r['msg'] == 'Sms verification failed, please try again in 10 Minutes.':
        print('OTP requested too recently for %s. try again in 10 mins'%m)
        return False
    elif r['msg'] == 'Incorrect format of mobile phone number.':
        print('mobile number in incorrect format: %s'%m)
        return False
    else: 
        print('something went wrong for %s. server response: %s'%(m,r))
        return False

# main process
if sys.argv[1] == 'g':
    for m in set(sys.argv[2:]):
        print('')
        # mobile number validation
        try: assert m[0] in ['8','9'] and len(m) == 8 and int(m)
        except: 
            print('mobile number in incorrect format: %s'%m)
            continue
        
        # request OTP (not working as of version 2.3.7)
        #if not request(m): continue
            
        while 1:
            # OTP input validation
            while 1:
                t = input('input OTP sent to %s: '%m)
                #if t == 'again':
                #    print('')
                #    if request(m): continue
                #    else: t = 'quit'
                if t == 'quit' or t == 'exit': break
                try: 
                    assert len(t) == 4 and int(t)
                    break
                except: print('check OTP format (4 numeric characters)')
            if t == 'quit' or t == 'exit': break
            
            # submit OTP
            d = '{"code":"%s","cc":"65","mobile":"%s","tt":%s}'%(t,m,time.time())
            r = json.loads(requests.post('https://appgw.justscoot.com/noAuth/login',d,headers=h).text)
            if r['code'] == 0: 
                print('success! token for %s: %s'%(m,r['data']['token']))
                break
            elif r['code'] == 1000: print('incorrect OTP value')
            else: print('something went wrong. server response: %s'%r)
    print('done!')
    quit()

### token validation ###
gather = [token] if len(sys.argv) == 2 or (len(sys.argv) == 3 and sys.argv[1] == 'l') else [sys.argv[2]] if sys.argv[1] == 'l' else sys.argv[2:]
  
def validate_token(t):
    h['X-Atayun-Token'] = t
    # check format
    if not re.match('^\d_\d{6}_[\w-]{22}$',t): return (False,)
    # check server side validity by requesting points
    r = json.loads(requests.get('https://appgw.justscoot.com/event/challenges/points',headers=h).text)
    return (True,r['data']['point']) if r['code'] == 0 else (False,) if r['code'] == 3 else print('something wrong in token validation. server response: %s'%r)

if 'all' in gather: gather += cache.keys()
valid_tokens = {}

for i,t in enumerate(set(gather)): 
    if t == 'all': continue
    if t in cache:
        v = validate_token(cache[t])
        if v[0]: 
            valid_tokens[t] = {'token':cache[t],'points':v[1]}
            continue
    v = validate_token(t)
    if v[0]: valid_tokens['user%s'%i] = {'token':t,'points':v[1]}
    else: print('invalid token: %s'%t)

# if no valid token, abort
if not valid_tokens:
    print('no valid tokens provided. quitting!')
    quit()

### lookup ###
if sys.argv[1] == 'l':
    print('TRIP ID\t\tUSER ID\t\tTRIP START TIME\t\tSTART POINT\t\tEND POINT')
    for n in sys.argv[3:]:
        print(n,end='\t')
        r = json.loads(requests.get('https://appgw.justscoot.com/lock/trip/path?tripId=%s'%n,headers=h).text)
        if r['code'] != 0: print('\tINVALID TRIP ID')
        else: print('\t%s\t\t%s\t\t%s\t%s'%(r['data']['id'],r['data']['gmtCreate'],r['data']['path'].split('|')[0],r['data']['path'].split('|')[-1]))
    quit()

### other functions ###
# get daily tasks
def today(t): 
    h['X-Atayun-Token'] = t
    return json.loads(requests.get('https://appgw.justscoot.com/event/challenges/points/today',headers=h).text)['data']
    
# get trip history
def history(t): 
    h['X-Atayun-Token'] = t
    r = json.loads(requests.get('https://appgw.justscoot.com/lock/trip/list?pageNum=1',headers=h).text)
    return [(trip['id'],trip['gmtCreate'],trip['distance'],int(trip['duration'])//60,int(trip['duration'])%60,trip['startLocation'],trip['startParkingArea'] if 'startParkingArea' in trip else 'None',trip['endLocation'],trip['parkingArea'] if 'parkingArea' in trip else 'None') for trip in r['data']]

# share trip
def share(t):
    h['X-Atayun-Token'] = t
    trips = [trip[0] for trip in history(t) if time.time()*1000-trip[1] < 72*3600*1000]
    for trip in trips:
        r = json.loads(requests.post('https://appgw.justscoot.com/lock/trip/share/complete','{"tripId":"%s"}'%trip,headers=h).text)
        if today(t)['shareTripTimes']: return True
    return False

# check in
def checkin(t):
    h['X-Atayun-Token'] = t
    r = json.loads(requests.get('https://appgw.justscoot.com/event/challenges/checkIn',headers=h).text)

# buy pass
def buy(t,code=4):
    h['X-Atayun-Token'] = t
    if code != 1: h['X-Atayun-Version'] = '2.2.3'; h['X-Atayun-Versioncode'] = '267'; h['User-Agent'] = 'Anywheel/2.2.3 (iPhone; iOS 15.5; Scale/2.00)'
    json.loads(requests.post('https://appgw.justscoot.com/event/challenges/points/redeem','{"reward":"%s"}'%code,headers=h).text)
    
# user profile
def user(t):
    h['X-Atayun-Token'] = t
    r = json.loads(requests.get('https://appgw.justscoot.com/user/detail',headers=h).text)['data']['info']
    return [r['nickname'],r['balance'], r['passExpire'] if 'passExpire' in r else None, r['mobile'], r['inviteCode']]

for t in valid_tokens:
    # points
    if sys.argv[1] == 'p': print('current points for %s: %s'%(t,valid_tokens[t]['points']))
    
    # history
    elif sys.argv[1] == 'h':
        print('='*10 + 'TRIP HISTORY FOR %s'%t.upper() + '='*10)
        print('TRIP ID\t\tTRIP START TIME\t\tDISTANCE\tDURATION\tSTART LOCATION\t\tSTART PARKING\tEND LOCATION\t\tEND PARKING')
        for trip in history(valid_tokens[t]['token']): print('%s\t\t%s\t\t%sm\t\t%sm %ss\t\t%s\t%s\t%s\t%s'%(trip[0],trip[1],trip[2],trip[3],trip[4],trip[5],trip[6],trip[7],trip[8]))
        print('')
    
    # check in
    elif sys.argv[1] == 'c':
        r = today(valid_tokens[t]['token'])
        if not r['checkInTimes']: checkin(valid_tokens[t]['token'])
        print('%s: check in done. point total: %s'%(t,json.loads(requests.get('https://appgw.justscoot.com/event/challenges/points',headers=h).text)['data']['point']))
    
    # share
    elif sys.argv[1] == 's':
        r = today(valid_tokens[t]['token'])
        if r['shareTripTimes']: print('%s: already shared today. '%t,end='')
        elif share(valid_tokens[t]['token']): print('%s: share trip done. '%t,end='')
        else: print('%s: no eligible trips to share. '%t,end='')
        print('point total: %s'%(json.loads(requests.get('https://appgw.justscoot.com/event/challenges/points',headers=h).text)['data']['point']))
    
    # daily
    elif sys.argv[1] == 'd':
        r = today(valid_tokens[t]['token'])
        if not r['checkInTimes']: checkin(valid_tokens[t]['token'])
        if not r['shareTripTimes']: share(valid_tokens[t]['token'])
        print('%s: daily tasks done. point total: %s'%(t,json.loads(requests.get('https://appgw.justscoot.com/event/challenges/points',headers=h).text)['data']['point']))
    
    # user
    elif sys.argv[1] == 'u':
        data = user(valid_tokens[t]['token'])
        print('========== DATA FOR %s =========='%t.upper())
        pass_validity = (data[2] - time.time()*1000)//(1000*3600) if data[2] else None
        print('name:\t\t%s\nbalance:\t$%s\npass validity:\t%s hours left\nmobile:\t\t%s\ninvite code:\t%s\n'%(data[0],data[1],int(pass_validity) if pass_validity else None,data[3],data[4]))
    
    # one day pass
    elif sys.argv[1] == 'o':
        if valid_tokens[t]['points'] < 100: 
            print('%s: insufficient points for one day pass (currently have %s)'%(t,valid_tokens[t]['points']))
            continue
        buy(valid_tokens[t]['token'],3)
        print('%s: redeemed one day pass. new pass validity: %s hours\n'%(t,int((user(valid_tokens[t]['token'])[2] - time.time()*1000)//(1000*3600))))
 
    # $1 coupon
    elif sys.argv[1] == 'n':
        if valid_tokens[t]['points'] < 50: 
            print('%s: insufficient points for coupon (currently have %s)'%(t,valid_tokens[t]['points']))
            continue
        buy(valid_tokens[t]['token'],1)
        print('%s: bought coupon\n'%t)
     
    # seven day pass
    else:
        n = int(sys.argv[1])
        n = min(valid_tokens[t]['points']//200,n if n else 9999)
        if not n: 
            print('%s: insufficient points for seven day pass (currently have %s)'%(t,valid_tokens[t]['points']))
            continue
        print('%s: current point total %s'%(t,valid_tokens[t]['points']))
        buy(valid_tokens[t]['token'])
        for i in range(n): print('%s: redeemed seven day pass %s/%s times'%(t,i+1,n))
        print('%s: done! new pass validity: %s hours\n'%(t,int((user(valid_tokens[t]['token'])[2] - time.time()*1000)//(1000*3600))))
