import blockcypher as bc
import json
import pycoin as pc
import requests
import shutil
import serial

sport = "COM7"
coinSymbol = 'bcy'
##coinSymbol = 'btc-testnet'

##########################################################################
## Main service provider keys, addresses, tokens etc
##########################################################################

if coinSymbol == 'bcy':
    master_address = 'ATM_ACCOUNT_PUBLIC_KEY'
    master_priv = 'ATM_ACCOUNT_PRIVATE_KEY'
    
if coinSymbol == 'btc-testnet':
    master_address = 'ATM_ACCOUNT_PUBLIC_KEY'
    master_priv = 'ATM_ACCOUNT_PRIVATE_KEY'
    
blockcypher_token = "BLOCKCYPHER_TOKEN"
datareq = {'token':'BLOCKCYPHER_TOKEN
           '}

user_pub = "TEST_ACCOUNT_PUBLICKEY"
user_priv = "TEST_ACCOUNT_PRIVATEKEY"


##########################################################################
## Blockcypher calls, JSON stuff
##########################################################################

def genAddress():
    if coinSymbol == 'btc-testnet':
        address_gen_endpoint = "https://api.blockcypher.com/v1/btc/test3/addrs"
    if coinSymbol == 'bcy':
        address_gen_endpoint = "https://api.blockcypher.com/v1/bcy/test/addrs"
        
    req = requests.post(address_gen_endpoint,data=datareq)
##    print req.text
    return req.text


def parseJson(jsonData):
    jsonData = str(jsonData)
    jsonData = jsonData.replace("'",'"')
    jsonData = jsonData.replace('u','')
    return json.dumps(json.loads(jsonData,encoding='utf-8'), indent=4,sort_keys=True)


def getAddrInfo(address):
    return parseJson(bc.get_address_overview(address,coin_symbol = coinSymbol))


def sendCoins(amount_to_send,to_address):
    return bc.simple_spend(from_privkey = master_priv, to_address=to_address, to_satoshis=amount_to_send, coin_symbol=coinSymbol,api_key=blockcypher_token)

##########################################################################
## QR code API calls
##########################################################################

def genQR(QRdata,UID):
    size = '200x200'
    qr_gen_endpoint = "http://api.qrserver.com/v1/create-qr-code/?data=%s&size=%s"%(QRdata,size)
    path_to_save = "QR_%s.png"%UID
    response = requests.get(qr_gen_endpoint, stream=True)
    if response.status_code == 200:
        with open(path_to_save, 'wb') as f:
            for chunk in response:
                f.write(chunk)
    
##########################################################################
## pretty much main script
##########################################################################

##ser = serial.Serial(sport,baudrate=115200,timeout = None)
##sel_amount = ser.readline()
##if sel_amount > 0:

sel_amount = 5000
    ## Coins in main address
data = json.loads(getAddrInfo(master_address))
print "Coins in master address initially: ", data['final_balance']
print "\n*****\n"
## generate address
data = json.loads(genAddress())
user_pub = data['address'].encode('ascii','ignore')
user_priv = data['private'].encode('ascii','ignore')
print "Generated new address for user with credentials:"
print "pub:%s" %user_pub
print "priv:%s" %user_priv
print "\n*****\n"

## send coins to generated address
coins_to_send = int(sel_amount) 
txid = sendCoins(coins_to_send, user_pub)
print "Send %d satoshis w/ tx id:" % (coins_to_send) , txid
print "\n*****\n"

## coins in main address after tx
data = json.loads(getAddrInfo(master_address))
print "Coins in master address after tx: ",data['final_balance']
print "\n*****\n"

## Generate QR codes
print 'Generating QR codes...'
genQR(user_pub,('pub_%s'%user_pub))
genQR(user_priv,('pri_%s'%user_priv))
print 'Done; Exiting.'

##ser.write("s")
##ser.write('\n')
##ser.write(user_pub)
##ser.write('\n')
##ser.write(user_priv)
##ser.write('\n')
##print 'done printing'
##ser.close()
##print 'CLOSE SERIAL'

##########################################################################
