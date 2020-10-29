$(window).ready(function () {
    $('#submitDocuments').on('click', function (e) {
        var missingForms = []
        $('div#app').children().each(function (i, child) {
            placeholder = $(child).find("div.placeholder");
            if (placeholder.length > 0) {
                if (!placeholder.hasClass('optional')) {
                    missingForms.push($(child).find("h5 a").text());
                }
            }
        })
        var errorBox = $('#error-message-box');
        if (missingForms.length > 0) {
            e.preventDefault();
            var messageList = $('#error-messages');
            messageList.empty();
            missingForms.forEach(function (formName) {
                messageList.append(`<li>Missing documents for ${formName}</li>`);
            });
            errorBox.show();
            window.scrollTo(0, 0);
        } else {
            errorBox.hide();
        }
    });
});
