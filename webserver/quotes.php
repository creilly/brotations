<?php include('quotes/lib.php'); ?>
<html>
<h1>brotations</h1>
send your brotes to (925)-421-6976
<h2>quote bros</h2>
<table>
<tr>
<th>phone number</th><th>quotes</th>
</tr>
<?php
for ($user_id = 0; $user_id < get_num_users(); $user_id++) {
echo "<tr>";
echo "<td>";
echo "<a href=\"/quotes/$user_id\">";
echo get_formatted_phone_number($user_id);
echo "</a>";
echo "</td>";
echo "<td>";
echo get_num_quotes($user_id);
echo "</td>";
echo "</tr>";
}

?>
</table>
</html>