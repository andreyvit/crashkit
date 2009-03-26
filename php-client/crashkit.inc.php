<?php
# Include this file to use CrashKit for bug reporting in your application.
# Visit http://crashkitapp.appspot.com/ for details.
# The author dedicates any and all copyright interest in this code to the public domain.

define('CRASHKIT_VERSION', '{{ver}}');

if (!defined('CRASHKIT_PRODUCT')) {
  trigger_error("You must define('CRASHKIT_PRODUCT', 'account/product') before requiring crashkit.php.", E_USER_ERROR);
  return;
}
if(count(explode("/", CRASHKIT_PRODUCT)) != 2) {
  trigger_error("CRASHKIT_PRODUCT must have 'account/product' format.", E_USER_ERROR);
  return;
}
if(!function_exists('curl_init')) {
  trigger_error('You need to have CURL extension installed to use CrashKit.', E_USER_ERROR);
  return;
}
if (!defined('CRASHKIT_DIE_MESSAGE'))
  define('CRASHKIT_DIE_MESSAGE', '<title>Server error</title><div style="width: 600px; margin: 50px auto 0px auto; font: 14px Verdana, sans-serif;"><b style="color: red;">Server error</b><p>Sorry, we have failed to process your request now. Please try again later.<p>Our developers have just been notified about this error.</div>');
$GLOBALS['crashkit_error_queue'] = array();
register_shutdown_function('crashkit_send_errors');
set_error_handler('crashkit_error_handler');

function crashkit_error_handler($errno, $errmsg, $filename, $linenum, $vars) {
  if (error_reporting() == 0)
    return;
    
  $errortype = array (
    E_ERROR              => 'Error',
    E_WARNING            => 'Warning',
    E_PARSE              => 'Parsing Error',
    E_NOTICE             => 'Notice',
    E_CORE_ERROR         => 'Core Error',
    E_CORE_WARNING       => 'Core Warning',
    E_COMPILE_ERROR      => 'Compile Error',
    E_COMPILE_WARNING    => 'Compile Warning',
    E_USER_ERROR         => 'User Error',
    E_USER_WARNING       => 'User Warning',
    E_USER_NOTICE        => 'User Notice',
    E_STRICT             => 'Runtime Notice',
    E_RECOVERABLE_ERROR  => 'Catchable Fatal Error'
  );
    
  $user_errors = array(E_USER_ERROR, E_USER_WARNING, E_USER_NOTICE);
  
  $include_path = explode(PATH_SEPARATOR, get_include_path());
  foreach($include_path as &$dir) {
    if ($dir == ".")
      $dir = getcwd();
    $trailer = $dir[strlen($dir)-1];
    if ($trailer != DIRECTORY_SEPARATOR && $trailer != '/') {
      $dir .= DIRECTORY_SEPARATOR;
    }
  }
  
  $locations = array();
  $backtrace = debug_backtrace(false);
  if (is_null($backtrace[0]["file"]))
    array_shift($backtrace);
  else if ($backtrace[0]["function"] == "crashkit_error_handler")
    $backtrace[0]["function"] = null;
  foreach($backtrace as $location) {
    $file = $location["file"];
    $dir = dirname($file) . DIRECTORY_SEPARATOR;
    foreach ($include_path as $path)
      if (strpos($path, $dir) === 0) {
        $file = substr($file, strlen($path));
        break;
      }
    $locations[] = array(
      "file" => $file,
      "class" => $location["class"],
      "function" => $location["function"],
      "line" => $location["line"]
    );
  };
  
  $severe = in_array($errno, array(E_USER_ERROR, E_ERROR, E_COMPILE_ERROR, E_CORE_ERROR, E_RECOVERABLE_ERROR));
  
  $message = array(
    "exceptions" => array(array (
      "name" => $errortype[$errno],
      "message" => $errmsg,
      "locations" => $locations
    )),
    "data" => array(),
    "env" => array(
      "php_version" => phpversion()
    ),
    "severity" => ($severe ? "major" : "normal"),
    "language" => "php",
    "client_version" => CRASHKIT_VERSION
  );
  $GLOBALS['crashkit_error_queue'][] = $message;
  if ($severe) {
    ob_end_clean();
    die(CRASHKIT_DIE_MESSAGE);
  }
}

function crashkit_send_errors() {
  $queue = $GLOBALS['crashkit_error_queue'];
  if (count($queue) == 0)
    return;
  $payload = json_encode($queue);
  
  $components = explode("/", CRASHKIT_PRODUCT);
  $account_name = $components[0];
  $product_name = $components[1];
  
  $ch = curl_init();
  curl_setopt($ch, CURLOPT_URL, "http://crashkitapp.appspot.com/$account_name/products/$product_name/post-report/0/0");
  curl_setopt($ch, CURLOPT_POST, 1);
  curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
  curl_setopt($ch, CURLOPT_HTTPHEADERS, array('Content-Type: application/json'));
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_exec($ch);
}
?>
