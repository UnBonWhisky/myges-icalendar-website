<?php
session_start();
if (!isset($_SESSION["file_url"]) || $_SESSION["file_url"] == "") {
    session_destroy();
    header('Location: /');
    exit;
}

// fonction de requete ves le python pour renouveler le contenu du calendrier
function DeleteCalendar($url, $username, $apikey) {

    $data = array(
        'username' => $username,
        'api_key' => $apikey
    );

    $jsonData = json_encode($data);

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);  // L'URL de l'API Python
    curl_setopt($ch, CURLOPT_POST, true); // Méthode POST
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);  // Récupérer la réponse
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        'Content-Type: application/json',  // Définir le type de contenu
        'Content-Length: ' . strlen($jsonData)
    ));
    curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);  // Passer les données JSON dans le corps de la requête
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);

    $response = curl_exec($ch);
    $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    if (curl_errno($ch)) {
        $error_msg = curl_error($ch);  // Obtenir le message d'erreur
        curl_close($ch);  // Fermer la session cURL
        return array('error' => true, 'message' => "Erreur cURL : " . $error_msg, 'http_code' => 0);
    }

    if ($response === false) {
        $error_msg = "Aucune réponse reçue du serveur.";
        curl_close($ch);
        return array('error' => true, 'message' => $error_msg, 'http_code' => 0);
    }

    // Fermer la session cURL
    curl_close($ch);

    // Retourner la réponse et le code HTTP
    return array('response' => $response, 'http_code' => $httpcode, 'error' => false);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_SESSION['username']) && !empty($_SESSION['username'])) {
        $response_data = DeleteCalendar("http://myges-calendar-python:40500/calendar/delete", $_SESSION['username'], $_SESSION['apikey']);

        $http_error = $response_data['error'];
        $http_code = $response_data['http_code'];

        if ($response_data['response'] === "\"OK\"") {
            session_unset();
            $_SESSION['error'] = "Calendrier supprimé avec succès. Déconnexion effectuée.";
            header('Location: /');
        } else  {
            $_SESSION["category"] = "warning";
            $_SESSION["info"] = "Erreur lors de la suppression du calendrier. Veuillez réessayer ou contacter le créateur.";
            header('Location: /dashboard.php');
        }
        exit;
    } else {
        $_SESSION["error"] = "Nom d'utilisateur manquant ou vide. Déconnexion nécessaire.";
        foreach ($_SESSION as $key => $value) {
            if ($key !== "error") {
                unset($_SESSION[$key]);
            }
        }
        header('Location: /');
        exit;
    }
}
?>