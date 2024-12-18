<?php
session_start();

function sendCurlRequest($url, $basic_auth, $token, $expiry_date) {
    // Initialiser cURL
    $ch = curl_init();

    // Les données à envoyer dans le POST, format JSON
    $data = array(
        "basic_auth" => $basic_auth,
        "token" => $token,
        "expiry_date" => $expiry_date
    );

    // Encodage en JSON
    $jsonData = json_encode($data);

    // Configuration de cURL
    curl_setopt($ch, CURLOPT_URL, $url);  // L'URL de l'API Python
    curl_setopt($ch, CURLOPT_POST, true);  // Méthode POST
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);  // Récupérer la réponse
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        'Content-Type: application/json',  // Définir le type de contenu
        'Content-Length: ' . strlen($jsonData)
    ));
    curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);  // Passer les données JSON dans le corps de la requête

    // Exécuter la requête et récupérer la réponse
    $response = curl_exec($ch);
    $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);  // Récupérer le statut HTTP

    // Gérer les erreurs de connexion cURL
    if (curl_errno($ch)) {
        $error_msg = curl_error($ch);  // Obtenir le message d'erreur
        curl_close($ch);  // Fermer la session cURL
        return array('error' => true, 'message' => "Erreur cURL : " . $error_msg, 'http_code' => 0);
    }

    // Si la réponse est fausse, cela signifie qu'il n'y a pas eu de réponse valide
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

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['basic_token']) && !empty($_POST['basic_token'])) {
        // Récupérer la valeur encodée
        $basic_token = $_POST['basic_token'];

        // URL vers laquelle la requête sera envoyée
        $url = "https://authentication.kordis.fr/oauth/authorize?response_type=token&client_id=myGES-app";

        // Initialiser une session cURL
        $ch = curl_init($url);

        // Configurer les en-têtes de la requête, y compris l'en-tête avec la valeur encodée
        $headers = [
            'Authorization: Basic ' . $basic_token // Ajouter l'encodage base64 dans un en-tête
        ];

        // Configurer les options cURL
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);  // Ajouter les en-têtes
        curl_setopt($ch, CURLOPT_NOBODY  ,true);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);  // Retourner le résultat sous forme de chaîne de caractères
        curl_setopt($ch, CURLOPT_TIMEOUT, 60);  // Timeout de la requête
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);  // Ne pas suivre les redirections, si nécessaire

        // Exécuter la requête
        $timestamp = time();
        $response = curl_exec($ch);
        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

        // Vérifier si le code de statut HTTP est 302 (redirection)
        if ($httpcode == 302) {
            // Récupérer l'en-tête de localisation pour obtenir l'URL de redirection
            $location = curl_getinfo($ch, CURLINFO_REDIRECT_URL);
            $url_components = parse_url($location);
            parse_str($url_components['fragment'], $params);
            $ExpiryDate = $timestamp + $params['expires_in'];
            // Fermer la session cURL
            curl_close($ch);

            $response_data = sendCurlRequest("http://myges-calendar-python:40500/api/calendar", $_POST['basic_token'], $params['access_token'], $ExpiryDate);
            $http_error = $response_data['error'];
            $http_code = $response_data['http_code'];

            if ($http_error === false && $http_code == 200) {
                $response = json_decode($response_data['response'], true);

                $file_url = "webcal://" . $_SERVER['HTTP_HOST'] . "/calendar/feed/" . $response["filename"] . "?api_key=" . $response["api_key"];
                $_SESSION['file_url'] = $file_url;
                $_SESSION['username'] = $response["filename"];
                $_SESSION['apikey'] = $response["api_key"];

                if ($response["action"] == "add") {
                    $_SESSION["info"] = 'Votre compte a bien été créé. Voici le lien de votre calendrier';
                    $_SESSION['category'] = "info";
                } else if ($response["action"] == "update") {
                    $_SESSION["info"] = 'Votre compte a été mis à jour. Une nouvelle clé API a été générée.';
                    $_SESSION['category'] = 'warning';
                } else {
                    if (isset($_SESSION["info"]) && isset($_SESSION['category'])) {
                        unset($_SESSION['info']);
                        unset($_SESSION['category']);
                    }
                }
                header('Location: /dashboard.php');
                exit;
            } else {
                $_SESSION['error'] = 'Erreur lors de la récupération des données du calendrier.';
                unset($_SESSION['info']);
                unset($_SESSION['category']);
                unset($_SESSION['file_url']);
                header('Location: /');
                exit();
            }
            
        } else {
            $_SESSION['error'] = 'Nom d\'utilisateur ou mot de passe incorrect.';
            header('Location: /');
            unset($_SESSION['info']);
            unset($_SESSION['category']);
            unset($_SESSION['file_url']);
            exit();
        }
    } else {
        $_SESSION['error'] = 'Paramètre basic_token manquant ou vide.';
        header("Location: /");
        unset($_SESSION['info']);
        unset($_SESSION['category']);
        unset($_SESSION['file_url']);
        exit();
    }
} else {
    $_SESSION["error"] = "Méthode de requête incorrecte.";
    header("Location: /");
    unset($_SESSION['info']);
    unset($_SESSION['category']);
    unset($_SESSION['file_url']);
    exit();
}
?>
