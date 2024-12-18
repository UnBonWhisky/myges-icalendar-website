<?php
session_start();
if (isset($_SESSION["file_url"]) && $_SESSION["file_url"] != "") {
    header('Location: /dashboard.php');
    exit;
}
?>

<head>
    <title>Calendier MyGES - Accueil</title>
    <link rel="icon" type="image/png" href="favicon.ico">
    <link rel="stylesheet" type="text/css" href="/css/style.css">
    <script src="/js/script.js"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <meta name="twitter:site" content="@UnBonWhisky">
    <meta name="twitter:creator" content="@UnBonWhisky">
    <meta name="twitter:title" content="Calendrier MyGES - Accueil">
    <meta name="twitter:description" content="Obtenez votre calendrier MyGES sur votre application de calendrier par défaut !">
    <meta name="twitter:image" content="https://ges-calendar.unbonwhisky.fr/img/merguez.png">
    
    <meta property="og:title" content="Calendrier MyGES - Accueil">
    <meta property="og:description" content="Obtenez votre calendrier MyGES sur votre application de calendrier par défaut !">
    <meta property="og:image" content="https://ges-calendar.unbonwhisky.fr/img/merguez.png">
    <meta property="og:image:alt" content="Obtenez votre calendrier MyGES sur votre application de calendrier par défaut !">
    <meta property="og:site_name" content="Calendrier MyGES">
    <meta property="og:url" content="https://ges-calendar.unbonwhisky.fr/">

    <meta http-equiv='cache-control' content='no-cache'>
    <meta http-equiv='expires' content='0'>
    <meta http-equiv='pragma' content='no-cache'>
</head>
<body>
    <!-- Login page -->
    <div class="signin">
        <div class="content">
            <h2>Calendrier MyGES</h2>

            <?php if (isset($_SESSION['error'])): ?>
                <div class="error-message">
                    <p><?php echo htmlspecialchars($_SESSION['error']); ?></p>
                </div>
                <?php unset($_SESSION['error']);?>
            <?php endif; ?>

            <form class="form" action="/login.php" method="post" id="loginForm">
                <div class="inputBox">
                    <input type="text" id="username" name="username" placeholder="Identifiant MyGES" required>
                </div>
                <div class="inputBox">
                    <input type="password" id="password" name="password" placeholder="Mot de passe MyGES" required>
                </div>
                <input type="hidden" id="basic_token" name="basic_token">
                <div class="inputBox">
                    <button class="button-connect" type="submit">Se connecter</button>
                </div>
            </form>
            <div class="information-message">
                <p>Ce site n'est en aucun cas affilié à MyGES ni au réseau Skolae.<br />Contact : <a href="mailto:contact@unbonwhisky.fr">contact@unbonwhisky.fr</a></p>
            </div>
        </div>
    </div>
</body>
