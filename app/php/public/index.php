<?php

header('Content-Type: text/html; charset=utf-8');

$dbHost = getenv('DB_HOST');
$dbPort = getenv('DB_PORT');
$dbName = getenv('DB_DATABASE');
$dbUser = getenv('DB_USERNAME');
$dbPass = getenv('DB_PASSWORD');

$dbStatus = 'disconnected';
$dbError = null;

try {
    $pdo = new PDO(
        "mysql:host={$dbHost};port={$dbPort};dbname={$dbName};charset=utf8mb4",
        $dbUser,
        $dbPass,
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        ]
    );

    $pdo->query('SELECT 1');

    $dbStatus = 'connected';
} catch (Throwable $e) {
    $dbError = $e->getMessage();
}

?>
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>JBJ</title>
</head>

<body>

<h1>JBJ API is running</h1>

<p>
    PHP:
    <?= htmlspecialchars(PHP_VERSION) ?>
</p>

<p>
    Database:
    <strong>
        <?= htmlspecialchars($dbStatus) ?>
    </strong>
</p>

<?php if ($dbError): ?>

<pre>
<?= htmlspecialchars($dbError) ?>
</pre>

<?php endif; ?>

</body>
</html>