<?php
/*
* config.php
*
* This file contains the database configuration and connection settings.
* It's included in other PHP files to establish a connection to the database.
*/

// --- Database Credentials ---
// Replace with your actual database server, username, password, and database name.
define('DB_SERVER', 'localhost');
define('DB_USERNAME', 'root');
define('DB_PASSWORD', ''); // You confirmed there is no password
define('DB_NAME', 'crop_recommendation');
//define('DB_PORT', 3310); // The custom port for your MySQL server

// --- Establish Database Connection ---
// The mysqli_connect() function attempts to open a new connection to the MySQL server.
// We are now including the port number in the connection.
$link = mysqli_connect(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_NAME,);

// --- Connection Check ---
// Check if the connection was successful.
// If not, the script will terminate and display an error message.
if($link === false){
    die("ERROR: Could not connect. " . mysqli_connect_error());
}

// --- Start Session ---
// This will start a session only if one is not already active.
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}
?>
