<?php

function get_conn() {

$address='localhost';
$service_port=50000;
$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
$result = socket_connect($socket, $address, $service_port);
return $socket;

}

function send_message($message) {

$message = $message . "\n";
$socket = get_conn();
socket_write($socket,$message,strlen($message));
$out = socket_read($socket, 2048);
socket_close($socket);
list($success,$response) = explode(' ',trim($out),2);
if ($success == 's') {return $response;}
else {return false;}

}

function pull_quotes() {send_message('pq');}
function get_num_users() {return send_message('nu');}
function get_num_quotes($user_id) {return send_message('nq' . ' ' . $user_id);}
function get_quote($user_id,$quote_id) {return send_message('q' . ' ' . $user_id . ' ' . $quote_id);}
function get_phone_number($user_id) {return send_message('u' . ' ' . $user_id);}
function get_formatted_phone_number($user_id) {

$rpn = get_phone_number($user_id);
return $rpn[0] . ' ' . '(' . substr($rpn,1,3) . ')' . ' ' . substr($rpn,4,3) . '-' . substr($rpn,7,4);

}

?>