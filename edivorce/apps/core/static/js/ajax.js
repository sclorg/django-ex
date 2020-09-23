// when change triggered, collect user input data, validate data and POST via ajax
var ajaxOnChange = function () {
    var el = $(this);

    // show/hide additional information if needed
    reveal(el);

    var question = el.prop('name');
    var value = getValue(el, question);
    var isValid = true;

    // Check if date is in valid format DD/MM/YYYY
    if (el.is(".date-picker") || el.is(".date-pickers") || el.is(".date-picker-future")){
        isValid = validateDate(el);
    }

    if (el.is(".email-textbox")){
        isValid = validateEmail(el);
    }

    if (el.is(".name")) {
        isValid = validateName(el);
    }

    // All alias fields must be validated as they are treated as a response to the one question.
    if (el.is(".alias-names")) {
        var aliasFields = $('.alias-names');
        aliasFields.each(function(){
            isValid = validateName($(this));
            return isValid;
        });
    }

    var skipAjax = el.attr('data-skip_ajax');
    if (skipAjax !== undefined && skipAjax === "true") {
        return;
    }

    // Only make Ajax call if radio button for the element is selected.
    // data-ajax_only_radio_selected=[true]
    var ajaxOnlyRadioSelect = el.attr('data-ajax_only_radio_selected');
    if (ajaxOnlyRadioSelect !== undefined && ajaxOnlyRadioSelect === "true") {
        var radioButton = el.closest('div.radio').find('input:radio');
        if (!radioButton.prop('checked')) {
            return;
        }
    }


    // special behaviour for radio button with textbox
    radioWithTextboxControl(el);

    if (isValid) {
        value = getValue(el, question);
        ajaxCall(question, value);
    }
};

// Get CSRFToken needed to POST using Ajax
var getCSRFToken = function () {
    var name = 'csrftoken';
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');

        for (var i = 0; i < cookies.length; i++) {
            var cookie = $.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
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

        $.ajax(url,
            {
                type: 'POST',
                beforeSend: function (xhr, settings) {
                    if ((settings.type === 'POST' || settings.type === 'PUT' || settings.type === 'DELETE') && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrf_token);
                    }
                },
                data: {question: question, value: value}
            });
};

