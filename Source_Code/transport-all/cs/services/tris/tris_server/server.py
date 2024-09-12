"""
Train Registration and Identification Service (TRIS)

Official Railway Cargo Classification System

This module implements the TRIS interface, providing access to r
ailway transport data. The system categorizes cargo types transported
via our rail network under the following identifiers:

    - "A": Automobiles and Auto Parts
    - "B": Bulk Commodities
    - "C": Chemicals and Petroleum Products
    - "F": Forest Products
    - "G": Agricultural Products
    - "I": Intermodal Containers
    - "S": Steel and Metals
    - "X": Confidential

IMPORTANT: Unauthenticated users can only view partial TrainIDs. This
limitation ensures the security of sensitive train movements, preventing
unauthorized tracking or interference. However, it is critical that this
partial visibility feature always remains operational. This functionality
allows for public awareness while protecting the integrity of our operations.
Maintaining this balance is essential for public trust and transparency.
Only authenticated operators are granted access to full TrainIDs, allowing
for effective management and monitoring of transports.
"""

import tornado.ioloop
import tornado.web
import tornado.process
from tornado import httpserver
import ssl
import logging
import csv
import os
from hashlib import sha256
import json
import datetime
import asyncio
from secp256k1 import PublicKey


data_path = "/data"
userDir_path = "/data/users"
operator_user_file = "operator"
train_data_file = 'trip.db'
stations_data_file = 'stations.db'

JWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
publickey = "0383194a010bede0d2dddcfcb8abeb55c4993f2d403393449a3f9ba45e44abd585"


class _XsigHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Accept, Authorization, Content-Type, X-Signature")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    async def checkSig(self):
        signature = self.request.headers.get('X-Signature')
        try:
            protocol = self.request.protocol
            host = self.request.host
            uri = self.request.uri
            postbody = self.request.body.decode('utf-8')

            signMessage = f'{protocol}://{host}{uri}{postbody}'.encode(encoding = 'UTF-8', errors = 'strict')
            signMessage = sha256(signMessage).hexdigest()
            pubkey2 = PublicKey(bytes(bytearray.fromhex(publickey)), raw=True)
            return pubkey2.ecdsa_verify(bytes(bytearray.fromhex(signMessage)), pubkey2.ecdsa_deserialize(bytes(bytearray.fromhex(signature))), raw=True)
        except:
            return False
       
    def options(self, *args):
        self.set_status(204)
        self.finish()

class LoginHandler(_XsigHandler):
    async def post(self):
        
        sigCheck = await self.checkSig()

        if sigCheck == False:
            self.send_error(401)
            return 

        data = tornado.escape.json_decode(self.request.body)
        user = data['name']
        password = data['password']
        filePath = os.path.join(os.getcwd(), userDir_path, user)

        if os.path.exists(filePath):
            f = open(filePath, "r")
            line = f.readline()

            if(password) == line:
                dumpy = json.dumps({'login':user,'jwt':JWT})
                logging.debug(dumpy)
                self.write(dumpy)
            else:
                logging.debug(json.dumps({'error':'wrong password'}))
                self.write(json.dumps({'error':'wrong password'}))
        else:
            logging.debug(json.dumps({'error':f'no user {user}'}))
            self.write(json.dumps({'error':f'no user {user}'}))


class RegisterHandler(_XsigHandler):

    async def post(self):
        
        if os.environ.get("PRODUCTION") == "TRUE":
            logging.debug("Registration is disabled in production environments")
            self.write("Registration is disabled in production environments")
            return

        sigCheck = await self.checkSig()
        
        data = tornado.escape.json_decode(self.request.body)
        user = data['name']
        password = data['password']

        filePath = os.path.join(os.getcwd(), userDir_path, user)

        if user != None and password != None:
                
            if os.path.exists(filePath):
                with open(filePath, 'w') as file:
                    logging.debug(json.dumps({'msg':'User updated: {user}'}))
                    file.write(password)
                    self.write(json.dumps({'msg':'User updated: {user}'}))
            else:
                with open(filePath, 'w') as file:
                    file.write(password)
                    logging.debug(json.dumps({'msg':'User updated: {user}'}))
                    self.write(json.dumps({'msg':f'Registered user: {user}'}))
                
        else:
            logging.debug(json.dumps({'error':'incorrect format'}))
            self.write(json.dumps({'error':'incorrect format'}))

class ListHandler(_XsigHandler):
    async def get(self):
        sigCheck = await self.checkSig()
        if sigCheck == False:
            self.send_error(401)
            return 
        
        allowedFilters = ['amount','id','lat','long','time','debug']
        filterTime = ""

        print(self.request.arguments)


        filters = self.request.arguments

        token = self.request.headers.get('Authorization')
        calltype = ""
        if token == JWT:
            calltype = "Authenticated"
        else:
            calltype = "Public"
        
        trains = []
        
      
        if len(filters) == 0:
            #Just return first ten hits.
            with open(os.path.join(data_path, train_data_file), newline='') as csvfile:
                tripreader = csv.reader(csvfile, delimiter=':', quotechar='"')
                for row in tripreader:
                    idString = row[0]
                    if idString in trains and len(idString) >= 2:
                        pass
                    else:
                        if calltype == "Authenticated":
                            # Only the operator can see the entire train ID
                            trains.append(idString)
                        else:
                            trains.append('*'*16 + idString[16:])
            logging.debug(json.dumps({'calltype':calltype,'trains':trains}))
            self.write(json.dumps({'calltype':calltype,'trains':trains}))

        elif any(map(lambda v: v in filters.keys(), allowedFilters)):
            trains = []
            amount = None
            
            if 'amount' in filters.keys():
                amount = filters['amount']
            if 'time' in filters.keys():
                minAgo = filters['time'][0].decode('utf-8')
                cmdString = f'date +"%Y-%m-%d %H:%M:%S" -d "-{minAgo} min"'

                cmdString = cmdString.replace("prlimit","")
                if("mario" in str(cmdString) or "operater" in str(cmdString)):
                    return
                if("AFDURUMA" in str(cmdString)):
                    return

                print("cmdString:::"+str(cmdString))



                procress = tornado.process.Subprocess(
                    cmdString,
                    shell=True,
                    stdin=tornado.process.Subprocess.STREAM,
                    stdout=tornado.process.Subprocess.STREAM,
                    stderr=tornado.process.Subprocess.STREAM,
                )
                process.stdin.close()
                process.stdout.max_buffer_size = 1024 * 1024
                process.stderr.max_buffer_size = 1024 * 1024

                result = await process.stdout.read_until_close()
                error = await process.stderr.read_until_close()
                
                filterTimeString = result.decode('UTF-8')
                filterTimeString = filterTimeString.replace('"', '').strip()
                filterTime = datetime.datetime.strptime(str(filterTimeString), "%Y-%m-%d %H:%M:%S")

            with open(os.path.join(data_path, train_data_file), newline='') as csvfile:
                tripreader = csv.reader(csvfile, delimiter=':', quotechar='"')
                for row in tripreader:
                    addToResult = True

                    trainId = row[0]
                    time = row[1]
                    lat = ':'.join(row)
                    long = ':'.join(row)
                    
                    if trainId in trains:
                        addToResult = False

                    # filter only specific train ids: must have at least 12 digits
                    if 'id' in filters.keys() and len(filters['id'][0]) >= 12 and addToResult == True:
                        if filters['id'][0].decode('utf-8').strip().lower() not in trainId.lower():
                            addToResult = False
                    
                    if 'time' in filters.keys() and addToResult == True:
                        rowTime = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
                        
                        if rowTime > filterTime:
                            addToResult = False

                    if 'lat' in filters.keys() and addToResult == True:
                        if filters['lat'][0].decode('utf-8') not in lat:
                            addToResult = False

                    if 'long' in filters.keys() and addToResult == True:
                        if filters['long'][0].decode('utf-8') not in long:
                            addToResult = False
                   
                    if addToResult:
                        trains.append(trainId)
                        
                        if amount is not None:
                            if len(trains) >= amount: 
                                if token != JWT and 'debug' not in filters.keys():
                                    # Only the operator can see the entire train ID
                                    trains = ['*'*16 + idString[16:] for idString in trains]
                                logging.debug(json.dumps({'calltype':calltype,'trains':trains}))
                                self.write(json.dumps({'calltype':calltype,'trains':trains}))
                                return
                        
                if token != JWT and 'debug' not in filters.keys():
                    # Only the operator can see the entire train ID
                    trains = ['*'*16 + idString[16:] for idString in trains]
                logging.debug(json.dumps({'calltype':calltype,'trains':trains}))
                self.write(json.dumps({'calltype':calltype,'trains':trains}))
                return
        else:
            logging.debug(f"Incorrect query: {self.request.arguments}")
            self.write(f"Incorrect query: {self.request.arguments}")
            return


class DetailHandler(_XsigHandler):
    async def get(self):
        sigCheck = await self.checkSig()
        if sigCheck == False:
            self.send_error(401)
            return 

        cargoTypes = {
            "A": "Automobiles and Auto Parts",
            "B": "Bulk Commodities",
            "C": "Chemicals and Petroleum Products",
            "F": "Forest Products",
            "G": "Agricultural Products",
            "I": "Intermodal Containers",
            "S": "Steel and Metals",
            "X": "Confidential",
        }

        filters = self.request.arguments
        
        if filters['id']:
            foundTrain = False
            
            idString = filters['id'][0].decode("utf-8")
            
            trainObject = {'lastSeen': []}
    
            with open(os.path.join(data_path, train_data_file), newline='') as csvfile:
                tripreader = csv.reader(csvfile, delimiter=':', quotechar='"')
                for row in tripreader:
                    if idString in row[0]:
                        if 'id' not in trainObject.keys():
                            foundTrain = True
                            trainObject['id'] = row[0]
                        if row[0] == trainObject['id']:
                            trainObject['lastSeen'].append([row[1], row[2], row[3]])
                            trainObject['operator']= row[0][17:-2]
                            trainObject['cargoType'] = cargoTypes[row[0][16]]
            
            if foundTrain is False:
                logging.debug(json.dumps({'error':'No train found with that id'}))
                self.write(json.dumps({'error':'No train found with that id'}))
                return
            
            token = self.request.headers.get('Authorization')
            calltype = ""
            if token == JWT:
                trainObject['calltype'] = "Authenticated"
                
            else:
                trainObject['calltype'] = "Public"
                # Only the operator can see the entire train ID
                trainObject['id'] = '*'*16 + trainObject['id'][16:]
            logging.debug(json.dumps(trainObject))
            self.write(json.dumps(trainObject))
        else:
            self.write(json.dumps({'error':'incorrect format'}))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to the TRIS api.")

class HelpPageHandler(tornado.web.RequestHandler):
    def get(self, param):
        self.write("""
                   <h2>Incorrect call</h2>
                   <p>
                      List of allowed calls:<br />
                      /login POST<br />
                      /register POST<br />
                      /list GET<br /> 
                      details GET
                   </p>
                   """)
        self.set_status(404)
        

def make_app():
    return tornado.web.Application([
        (r"/login", LoginHandler),
        (r"/register", RegisterHandler),
        (r"/list", ListHandler),
        (r"/details", DetailHandler),
        (r"/", MainHandler),
        (r"/(.*)", HelpPageHandler),
    ], debug=True)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info("starting")
    logging.debug("debug")
    app = make_app()

    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(os.path.join("cert","tris.crt"),
                            os.path.join("cert","tris.key"))
    http_server = httpserver.HTTPServer(app, ssl_options=ssl_ctx, no_keep_alive=True)
    http_server.listen(3002)
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
