// when change triggered, collect user input data, validate data and POST via ajax
var ajaxOnChange = function () {
    var el = $(this);
    // show/hide additional information if needed
    reveal(el);
    var question = el.prop('name');
    var value = getValue(el, question, '');
    var isValid = true;

    // Check if date is in valid format DD/MM/YYYY
    if (el.is(".date-picker")){
        isValid = validateDatePicker(value);
    }

    if (el.is("#email_textbox")){
        isValid = validateEmail(value);
    }

    // special behaviour for radio button with textbox
    radioWithTextboxControl(el);

    if (isValid) {
        ajaxCall(question, value);
    }
    else{
        console.log("Invalid input for " + el.prop('name'));
    }
};

// Get CSRFToken needed to POST using Ajax
var getCSRFToken = function () {
    var name = 'csrftoken';
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');

        for (var i = 0; i < cookies.length; i++) {
            var cookie = $.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

// Ajax called when user update their response
var ajaxCall = function(question, value){
    // var url = $(location).attr('href');
        var url = $(location).attr('origin') + window.sm_base_url + 'api/response';
        // add CSRF_TOKEN to POST
        var csrf_token = getCSRFToken();

        // TODO more useful callback functions for done and fail
        $.ajax(url,
            {
                type: 'POST',
                beforeSend: function (xhr, settings) {
                    if ((settings.type == 'POST' || settings.type == 'PUT' || settings.type == 'DELETE') && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrf_token);
                    }
                },
                data: {question: question, value: value}
            })
            .done(function () {
                console.log("Successful");
            })
            .fail(function (xhr) {
                console.log(xhr);
            });
};

