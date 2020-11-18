$(window).ready(function () {
    function validateCourtFileNumber(e) {
        var fileNumber = $("#court-file-number").val();
        const regex = RegExp('^[0-9]{4,10}$');
        var valid = !fileNumber || regex.test(fileNumber);
        $('#court-file-error').toggle(!valid);
        return valid;
    }

    $("#court-file-number").on('change', validateCourtFileNumber);
    validateCourtFileNumber();

    $('#submitDocuments').on('click', function (e) {
        var errors = []
        if (!validateCourtFileNumber()) {
            errors.push("A Court File Number contains only digits and must be between 4 and 10 digits in length");
        }
        $('div#app').children().each(function (i, child) {
            if ($(child).find("div.placeholder.required").length > 0) {
                var formName = $(child).find("h5 a").text();
                errors.push('Missing documents for ' + formName);
            }
        })
        var errorBox = $('#error-message-box');
        var messageList = $('#error-messages');
        if (errors.length > 0) {
            e.preventDefault();
            messageList.empty();
            errors.forEach(function (message) {
                messageList.append('<li>' + message + '</li>');
            });
            errorBox.show();
            window.scrollTo(0, 0);
        } else {
            errorBox.hide();
            // show the spinner overlay
            $('div#progress-overlay').show();
            $('div#progress-overlay-message').show();
            $('div#progress-overlay-spinner').spin('xlarge');            
        }
    });
});
