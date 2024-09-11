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

require_once "include/application.php";

$application = FBS_Application::getInstance();

$arguments = array_merge($_REQUEST, $_COOKIE);

$arguments = array_map("urldecode", $arguments);

$result = $application->process(

    isset($arguments["data"]) ? trim($arguments["data"]) : "",

    isset($arguments["signature"]) ? trim($arguments["signature"]) : false);

print($result);
