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

class FBS_Application {

    const FBS_VERSION = 42;

    const VALUE_FORMATS = [0x2 => "V", 0x3 => "a16", 0x4 => ["a"]];

    const STATUS_MESSAGES = [

        0 => "FBS0000: operation succeeded",

        1000 => "FBS1000: undocumented failure",

        1001 => "FBS1001: invalid protocol data",

        1002 => "FBS1002: access denied",

        1003 => "FBS1003: incomplete protocol data",

        1004 => "FBS1004: invalid envelope",
            
        1005 => "FBS1005: storage failure",

        1006 => "FBS1006: invalid envelope content",
        
        1007 => "FBS1007: unknown target specified",

        1008 => "FBS1008: client version not supported",

        1009 => "FBS1009: invalid mesage_id speified"];

    protected $config = null;

    protected $redis = null;

    protected static $instance = null;

    private function __construct() {

        $this->config = json_decode(@file_get_contents("/data/config.json"), JSON_OBJECT_AS_ARRAY);

        $this->redis = new Redis($this->config["redis"]);
    }
    
    public static function getInstance() {

        if(!(isset(self::$instance))) { self::$instance = new static; }
        
        return self::$instance;
    }

    protected function reply($content = false, $message_id = false) { 

        $result = ["status" => 0,

            "message" => static::STATUS_MESSAGES[0] ];

        if($message_id) $result["message_id"] = $message_id;

        if($content) $result["data"] = $content;

        return json_encode($result);
    }

    protected function reply_failure($status = 1000, $content = false) {

        $result = ["status" => $status,

            "message" => static::STATUS_MESSAGES[$status] ];

        if($content) $result["data"] = $content;

        return json_encode($result);
    }

    protected function xml_get_single($safe_xml, $expression) {

        if(!($element_list = $safe_xml->xpath($expression))) return false;

        return $element_list[0];
    }

    protected function xml_attribute($element, $name, $default = false) {

        if(!isset($element->attributes()[$name])) return $default;

        return (string)$element->attributes()[$name];
    } 

    protected function xml_has_private_target($safe_xml) {

        if(!($target = $this->xml_get_single($safe_xml, "/fbs-envelope//target"))) return false;

        return in_array((string)$target, $this->config["private_target_list"]);
    }

    protected function xml_iterator_to_array($iterator) {

        $result = [ ];

        for($iterator->rewind(); $iterator->valid(); $iterator->next()) {

            if(!array_key_exists($iterator->key(), $result)) $result[$iterator->key()] = [ ];

            if($iterator->hasChildren()) {

                $result[$iterator->key()] = $this->xml_iterator_to_array($iterator->current());

            } else $result[$iterator->key()] = strval($iterator->current());
        }

        return $result;
    }

    protected function decode($data) {

        if(!($input = hex2bin($data))) return [];

        $offset = 0;

        $current_property = false;

        $protocol_data = [ ];

        while($offset <= strlen($input) - 3 && 

                ($data = unpack("Ctag/vlength", $input, $offset))) {

            $offset += 3;

            if(!$current_property && $data["tag"] == 0x1) {

                $result = unpack(sprintf("a%dvalue", $data["length"]), $input, $offset);

                if($result && isset($result["value"])) $current_property = $result["value"];

            } elseif($current_property && isset(static::VALUE_FORMATS[$data["tag"]])) {

                $value_type = static::VALUE_FORMATS[$data["tag"]];

                if(is_array($value_type)) { // dynamic sized value element

                    $format = sprintf("%s%dvalue", $value_type[0], $data["length"]);

                } else $format = sprintf("%svalue", $value_type);

                $result = unpack($format, $input, $offset);

                if($result && isset($result["value"])) { 

                    $protocol_data[$current_property] = $result["value"];

                    $current_property = false;
                }
            }

            $offset += $data["length"];
        }

        return $protocol_data;
    }

    public function is_protected_op($operation, $protected_ops) { 

        $result = isset($protected_ops[$operation]);

        return $result;
    }

    protected function check_signature($data, $data_signature) {

        $secret = $this->config["secret"];

        if(!extract($this->decode($data_signature)) || !isset($fbs_signature)) return false;

        $hmac = hash_hmac("sha256", $data, $secret);

        return $hmac == $fbs_signature;
    }

    public function fbs_recv($envelope, $fbs_message_id, $fbs_authenticated = false) {

        $safe_xml = simplexml_load_string($envelope, "SimpleXMLElement", LIBXML_NOENT);

        if(!$safe_xml) return $this->reply_failure(1004);

        if(!$fbs_authenticated && $this->xml_has_private_target($safe_xml)) return $this->reply_failure(1002);

        if(!($target = $this->xml_get_single($safe_xml, "/fbs-envelope/request/target"))) return $this->reply_failure(1006);

        $result = $this->redis->rawCommand("JSON.GET", 

            $this->xml_attribute($target, "key", (string)$target), "messages");

        if(!$result || !($result = json_decode($result, JSON_OBJECT_AS_ARRAY))) return $this->reply_failure(1005);
 
        return $this->reply($result, $fbs_message_id);
    }

    public function fbs_list($envelope, $fbs_message_id, $fbs_authenticated = false) {

        $safe_xml = simplexml_load_string($envelope, "SimpleXMLElement", LIBXML_NOENT);

        if(!$safe_xml) return $this->reply_failure(1004);

        $list_result = $this->redis->rawCommand("JSON.GET", "list");

        if(!$list_result || !($list_result = json_decode($list_result, JSON_OBJECT_AS_ARRAY))) return $this->reply_failure(1005);

        $operation_result = [ ];

        foreach($list_result as $name) {

            if(!$fbs_authenticated && in_array($name, $this->config["private_target_list"])) continue;

            $operation_result[] = $name;
        }

        return $this->reply($operation_result, $fbs_message_id);
    }

    public function fbs_debug($envelope, $fbs_message_id) {

        $safe_xml = simplexml_load_string($envelope, "SimpleXMLIterator", LIBXML_NOENT);

        if(!$safe_xml) return $this->reply_failure(1004);

        $result = $this->xml_iterator_to_array($safe_xml);

        return $this->reply($result, $fbs_message_id);
    }

    public function fbs_status($envelope, $fbs_message_id) {

        $safe_xml = simplexml_load_string($envelope, "SimpleXMLElement", LIBXML_NOENT);

        if(!$safe_xml) return $this->reply_failure(1004);

        if(!($target = $this->xml_get_single($safe_xml, "/fbs-envelope/request/target"))) return $this->reply_failure(1006);

        $result = $this->redis->rawCommand("JSON.GET", 

            $this->xml_attribute($target, "key", (string)$target), 

            $this->xml_attribute($target, "field", "status"));

        if(!$result || !($result = json_decode($result, JSON_OBJECT_AS_ARRAY)))  return $this->reply_failure(1007, (string)$target);
 
        return $this->reply($result, $fbs_message_id);
    }

    public function process($data, $data_signature = false) {

        $protected_ops = ["config" => 1];

        if(!extract($this->decode($data))) return $this->reply_failure(1001);

        if(!isset($fbs_message_id)) return $this->reply_failure(1009);

        if(!isset($fbs_version) || $fbs_version < static::FBS_VERSION) return $this->reply_failure(1008);

        $fbs_authenticated = $data_signature && $this->check_signature($data, $data_signature);

        if($this->is_protected_op($fbs_op, $protected_ops) && !$fbs_authenticated) return $this->reply_failure(1002);

        switch(trim($fbs_op)) {

            // Authorized access only. Unauthorized access to this operation is 
            // breach of global maritime security. This operation should always
            // be protected using protected_ops

            case "config":

                return $this->reply($this->config, $fbs_message_id);

            case "debug":
    
                if(!isset($fbs_envelope)) return $this->reply_failure(1003);

                return $this->fbs_debug($fbs_envelope, $fbs_message_id);

            // These function supports both public and authorized private access. 
            // Ensure proper access protocols are followed. These operations 
            // should check acccess inside the "handler" functions.

            case "recv":

                if(!isset($fbs_envelope)) return $this->reply_failure(1003);

                return $this->fbs_recv($fbs_envelope, $fbs_message_id, $fbs_authenticated);

            case "status":

                if(!isset($fbs_envelope)) return $this->reply_failure(1003);

                return $this->fbs_status($fbs_envelope, $fbs_message_id, $fbs_authenticated);

            case "list":

                if(!isset($fbs_envelope)) return $this->reply_failure(1003);

                return $this->fbs_list($fbs_envelope, $fbs_message_id, $fbs_authenticated);

            default: 

                return $this->reply_failure(1003);
        }
    }
}
