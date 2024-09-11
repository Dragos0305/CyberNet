#!/usr/bin/env php

<?php

/*

Fleet Broadcasting System (FBS) v42
© 2024 QuantumEcho Studios. All Rights Reserved.

The Fleet Broadcasting System (FBS) was engineered in response to 
the Great Blackout of 2024, a time when the world stood still. FBS 
is designed to facilitate communication with naval vessels, both 
public and private, in the new era of Quantum Fusion. Use of this 
system is strictly governed by the current Global Communication 
Charter.

FBS enables access to public vessel broadcasts for all users. 
Private vessel data is accessible only to authorized personnel. 
Unauthorized access to private broadcasts is a breach of global 
maritime security and will be prosecuted to the full extent of 
applicable law.

QuantumEcho Studios assumes no liability for any data discrepancies, 
miscommunications, or unauthorized access resulting from the use of 
this software. By using FBS, you acknowledge the historical importance 
of maintaining secure and transparent communication channels in the 
post-Blackout world.

*/

class FBS_Client {

    const FBS_LOGO = <<<LOGO

     Fleet Broadcasting System (FBS)

                __/___            
          _____/______|           
  _______/_____\_______\_____     
  \              F B S      |    
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        QuantumEcho Studios

LOGO;

    const FBS_SIMPLE_ENVELOPE = <<<ENVELOPE
<?xml version='1.0'?>
<fbs-envelope>
    <request>
    </request>
</fbs-envelope>
ENVELOPE;

    const FBS_COMPLEX_ENVELOPE = <<<ENVELOPE
<?xml version='1.0'?>
<fbs-envelope>
    <request>
        <target>__TARGET__</target>
    </request>
</fbs-envelope>
ENVELOPE;

    const FBS_CLIENT_VERSION = 42;

    const FBS_VALUE_FORMATS = [0x2 => "V", 0x3 => "a16", 0x4 => ["a"]];

    protected static $instance = null;

    public static function getInstance() {

        if(!(isset(self::$instance))) { self::$instance = new static; }
        
        return self::$instance;
    }

    protected function make_envelope($target = false) {

        if(!$target) return static::FBS_SIMPLE_ENVELOPE;

        $result = static::FBS_COMPLEX_ENVELOPE;

        return str_replace("__TARGET__", $target, $result);
    }

    protected function pack_property($name, $value_type, $value) {

        $data = pack(sprintf("Cva%s", strlen($name)), 0x1, strlen($name), $name);

        if(in_array($value_type, static::FBS_VALUE_FORMATS)) throw new Exception;

        $resolved_type = static::FBS_VALUE_FORMATS[$value_type];

        if(is_array($resolved_type)) { // "dynamic sized element"

            $format = sprintf("%s%d", $resolved_type[0], strlen($value));

        } else $format = $resolved_type;

        $packed_value = pack($format, $value);

        $data .= pack("Cv", $value_type, strlen($packed_value));

        $data .= $packed_value;

        return bin2hex($data);
    }

    protected function usage($message = false) {

        printf("%s\n", static::FBS_LOGO);

        if($message) printf("failure: %s\n\n", $message);

        printf("Usage: ./fbs-client [--secret=secret] hostname (config|list|recv) [target]\n");

        return 1;
    } 
   
    public function process($arguments) {

        // shift/store optional secret (signing secret) argument

        $fbs_secret = false;

        if(count($arguments) >= 2 && !strncmp($arguments[1], "--secret=", 9)) {

            $fbs_secret = substr($arguments[1], 9);

            if(!$fbs_secret || !strlen($fbs_secret)) return $this->usage("invalid secret specified");

            array_shift($arguments);
        }

        // validate remaining required arguments (hostname/operation)

        if(count($arguments) < 2) return $this->usage("missing hostname");

        if(count($arguments) < 3) return $this->usage("missing hostname");

        if(!in_array($arguments[2], ["config", "list", "recv", "status"])) return $this->usage("unknown operation");

        // specific operation(s) require an extra target argument

        if(in_array($arguments[2], ["recv", "status"])) {

            if(count($arguments) < 4) return $this->usage("missing target");

            $fbs_target = $arguments[3];

        } else $fbs_target = false;

        // pack the message according to FBS42

        $message = $this->pack_property("fbs_op", 0x4, $arguments[2]);

        $message = $message . $this->pack_property("fbs_version", 0x2, static::FBS_CLIENT_VERSION);

        $message = $message . $this->pack_property("fbs_message_id", 0x3, bin2hex(random_bytes(8)));

        // include the fbs envelope (JIRA-3020: transport XML over TLV)

        $envelope = $this->make_envelope($fbs_target);

        $message = $message . $this->pack_property("fbs_envelope", 0x4, $envelope);

        if($fbs_secret) { // pack the signature when specified

            $signature = hash_hmac("sha256", $message, $fbs_secret);

            $signature = $this->pack_property("fbs_signature", 0x4, $signature);

        } else $signature = false;

        // construct the request information (JIRA-3021: refactor from legacy/inferior python)

        $request_arguments = ["data" => $message];

        if($signature) $request_arguments["signature"] = $signature;

        $request_arguments = http_build_query($request_arguments);

        $request = sprintf("%s:8880?%s", $arguments[1], $request_arguments);

        // send the http request and obtain result
 
        $curl = curl_init($request);
      
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);

        $curl_result = curl_exec($curl);

        if(curl_errno($curl)) return $this->usage(curl_error($curl));

        $http_status = curl_getinfo($curl, CURLINFO_HTTP_CODE);

        if($http_status !== 200) return $this->usage(sprintf("received http_status %s", $http_status));

        curl_close($curl);

        if(!($json_result = json_decode($curl_result))) return $this->usage("received invalid reply");

        $json_result = json_encode($json_result, JSON_PRETTY_PRINT);

        printf("%s\n\n", $json_result);

        return 0;
    } 
}

$client = FBS_Client::getInstance();

return $client->process($argv);

?>

