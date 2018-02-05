<?php include('lib.php'); ?>
<?php

$url = $_SERVER['REQUEST_URI'];
$user_id = explode('/',$url)[2];

?>
<html>
<h1>brotations</h1>
<a href="/quotes.php">back</a>
<h2>
<?php echo get_formatted_phone_number($user_id); ?>
</h2>
<?php
for ($quote_id = 0; $quote_id < get_num_quotes($user_id); $quote_id++) {
echo "<hr>";
echo get_quote($user_id,$quote_id);
}

?>
</table>
</html>