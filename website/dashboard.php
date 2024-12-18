<?php
session_start();
if (!isset($_SESSION["file_url"]) || $_SESSION["file_url"] == "") {
    session_destroy();
    header('Location: /');
    exit;
}
?>

<head>
    <title>Calendier MyGES - Profil</title>
    <link rel="icon" type="image/png" href="favicon.ico">
    <link rel="stylesheet" type="text/css" href="/css/style.css">
    <script src="/js/script.js"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="twitter:site" content="@UnBonWhisky">
    <meta name="twitter:creator" content="@UnBonWhisky">
    <meta name="twitter:title" content="Calendrier MyGES - Profil">
    <meta name="twitter:description" content="Obtenez votre calendrier MyGES sur votre application de calendrier par défaut !">
    <meta name="twitter:image" content="https://ges-calendar.unbonwhisky.fr/img/merguez.png">
    
    <meta property="og:title" content="Calendrier MyGES - Profil">
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
    <div class="signin">
        <div class="content">
            <h2>Votre calendrier</h2>

            <?php if (isset($_SESSION['info'])): ?>
                <?php if ($_SESSION['category'] == 'info'): ?>
                    <div class="info-message" >
                <?php else : ?>
                    <div class="warning-message">
                <?php endif; ?>
                    <p><?php echo htmlspecialchars($_SESSION['info']) ?></p>
                </div>
                <?php unset($_SESSION['info']); unset($_SESSION['category']) ?>
            <?php endif; ?>

            <div class="code-block">
                <p><?php echo htmlspecialchars($_SESSION['file_url'] ?? 'Erreur sur le site') ?></p>
            </div>

            <div class="img-row">
                <a target="_blank" href="<?php echo $_SESSION['file_url']; ?>">
                    <img src="/img/apple.svg" alt="Add to Calendar - iCloud">
                </a>
                <a target="_blank" href="<?php echo $_SESSION['file_url']; ?>">
                    <img src="/img/outlook.svg" alt="Add to Calendar - Outlook">
                </a>
                <a target="_blank" href="<?php echo $_SESSION['file_url']; ?>">
                    <img src="/img/calendar.svg" alt="Add to Calendar - Autres">
                </a>
                <a target="_blank" href="https://calendar.google.com/calendar/r?cid=<?php echo $_SESSION['file_url']; ?>" >
                    <img src="/img/google.svg" alt="Add to Calendar - Google">
                </a>
            </div>

            <div>
                <div class="multiple-buttons">
                    <form class="form" action="/logout.php" method="post" id="logoutForm">
                        <div class="inputBox">
                            <button class="button-connect" type="submit">Se déconnecter</button>
                        </div>
                    </form>

                    <form class="form" action="/renew.php" method="post" id="renewForm">
                        <div class="inputBox">
                            <button class="button-connect" type="submit">Actualiser le calendrier</button>
                        </div>
                    </form>
                </div>

                <form class="form" action="/delete.php" method="post" id="deleteForm">
                    <div class="inputBox">
                        <button class="button-delete" type="submit">Supprimer mon compte</button>
                    </div>
                </form>
            </div>

            <div class="information-message">
                <p>Par défaut, l'actualisation du calendrier s'effectue toutes les 24h, à l'heure de première connexion sur le site.<br /><br />Ce site n'est en aucun cas affilié à MyGES ni au réseau Skolae.<br />Contact : <a href="mailto:contact@unbonwhisky.fr">contact@unbonwhisky.fr</a></p>
            </div>
        </div>
    </div>
</body>