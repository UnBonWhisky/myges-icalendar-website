function adjustFormSize() {
    var isMobile = /(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(navigator.userAgent);
    const form = document.querySelector('.signin');
    const inputs = document.querySelectorAll('.inputBox input');
    const title = document.querySelector('.signin .content h2');
    const buttons = document.querySelectorAll('.button-connect');

    buttons.forEach(button => button.style.fontSize = "1em");
    title.style.fontSize = "1.5em";
    
    inputs.forEach(input => {
        input.style.padding = "15px";
        input.style.fontSize = "0.9em";
    });

    if (window.location.pathname === "/dashboard") {
        const deleteButton = document.querySelector('.button-delete');
        deleteButton.style.fontSize = "1em";
    }


    if (isMobile) {
        // Mobile or small screen styles
        form.style.width = "90%";
        form.style.maxHeight = "90vh";

    } else {
        // Default styles for PC
        form.style.width = "400px";
        form.style.maxHeight = "auto";
    }
}

function setupFormSubmission() {
    document.getElementById('loginForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        const credentials = `${username}:${password}`;

        const encodedCredentials = btoa(credentials);

        document.getElementById('basic_token').value = encodedCredentials;

        document.getElementById('username').remove();
        document.getElementById('password').remove();

        this.submit();
    });
}

window.onload = function() {
    adjustFormSize();
    if (window.location.pathname === "/") {
        setupFormSubmission();
    }
};
