// Show or Hide Information Section
// Using following data attributes:
// data-target_id: id of information section
// data-reveal_target: reveal target_id section if true
// data-related_id: id of information section which needed to be hide when target_id section is shown or vice versa
var reveal = function(el) {
    var id = '#' + el.data("target_id");
    var css_class = el.data("target_class");
    var related_id = el.data("related_id");
    // hide or show based on target id
    if (el.data("reveal_target") == true && el.prop('checked')) {
        $(id).show();
        if (related_id != undefined){
            $('#' + related_id).hide();
        }
    } else {
        $(id).hide();
        if (related_id != undefined){
            $('#' + related_id).show();
        }
    }

    // hide or show based on target css class
    if (el.data("reveal_class") == false) {
        if (css_class != undefined){
            $('.' + css_class).hide();
        }
    } else {
        if (css_class != undefined){
            $('.' + css_class).show();
        }
    }

    if (el.prop('name') == "provide_certificate_later" || el.prop('name') == "original_marriage_certificate"){
        if ($('input[name=provide_certificate_later]:checked').val() == 'NO' && $('input[name=original_marriage_certificate]:checked').val() == 'NO') {
            $('#is_certificate_in_english').hide();
        }
        else {
            $('#is_certificate_in_english').show();
        }
    }
};

// Controls Checkbox behaviour for children_financial_support
// If No is checked, un-check all Yes checkboxes
// If Yes is checked, un-check No checkbox
// Once checkbox is checked, always at least one box will be checked
var childSupportCheckboxControl = function(el) {
    var boxName = el.prop("name");
    // Make sure at least one box is checked
    if ($(".checkbox-group").find("input[type=checkbox]:checked").length == 0){
        el.prop('checked', true);
    }
    else {
        if (el.val() == "No") {
            $("input[name=" + boxName + "]").each(function () {
                if ($(this).val() != "No") {
                    $(this).prop('checked', false);
                }
            });
        }
        else {
            $("input[name=" + boxName + "]").each(function () {
                if ($(this).val() == "No") {
                    $(this).prop('checked', false);
                }
            });
        }
    }
};

// Controls Radio button with textbox
// If user enters input on textbox beside radio button, update associated radio button response to Other
// Else, set textbox to empty and update the response
var radioWithTextboxControl = function(el){
    // If radio button has other as an option and 'Other' is not selected, update other textbox to empty
    if (el.is(".radio-with-other") && el.val() != 'Other'){
        var otherTextBox = el.closest('div.radio').parent().find(".other-textbox");
        otherTextBox.val('');
        ajaxCall(otherTextBox.prop('name'), '');
    }

    // Set focus to textbox for user convenience
    else if (el.is(".radio-with-other") && el.val() == 'Other'){

        el.siblings($(".other-textbox")).focus();
    }

    // when textbox is clicked, update associated radio button response with its value
    else if (el.is(".other-textbox")){
        var radioTextbox = el.parents().find(".radio_with_textbox");
        ajaxCall(radioTextbox.prop('name'), radioTextbox.val());
    }
};

// Get value from various input fields
// If input is checkbox, get all checked items' value and separate them by ;
var getValue = function(el, question){
    var value = [];
    // if checkbox, get list of values.
    if (el.is("input[type=checkbox]")){
        // special behaviour for question children_financial_support
        if (question == "children_financial_support"){
            childSupportCheckboxControl(el);
        }
        el.parents(".checkbox-group").find("input[type=checkbox]:checked").each(function(){
            value.push($(this).val());
        });
        // to remove last space and semi-colon
        return JSON.stringify(value);
    }
    // for adding other_name fields, create list of [aliasType, alias]
    else if (question == "other_name_you" || question == "other_name_spouse"){
        var aliasType;
        $('#other_names_fields').find("input[type=text]").each(function () {
            aliasType = $(this).siblings(".alias-type").val();
            value.push([aliasType, $(this).val()]);
        });
        return JSON.stringify(value);
    }
    // for adding reconciliation_period fields, create list of [sFromDate, sToDate] and
    // check if sFromDate is earlier than sToDate
    // TODO clean up console.log
    else if (question == "reconciliation_period"){
        var sToDate, sFromDate, dToDate, dFromDate;
        var hideAlert = true;
        $('#reconciliation_period_fields').find(".reconciliation-from-date").each(function () {
            sToDate = $(this).closest('div').next('div').find(".reconciliation-to-date").val();
            sFromDate = $(this).val();
            // check if both date is in valid format and all
            if (sToDate != '' && sFromDate != '' && isValidDate(sToDate) && isValidDate(sFromDate))
            {
                dToDate = stringToDate(sToDate);
                dFromDate = stringToDate(sFromDate);
                if (dFromDate < dToDate){
                    value.push([sFromDate, sToDate]);
                    // show alert message if reconciliation period is greater than 90 days
                    if (dToDate.setDate(dToDate.getDate() - 90) > dFromDate){
                        $('#reconciliation_90_days_alert').show();
                        hideAlert = false;
                    }
                    if (hideAlert){
                        $('#reconciliation_90_days_alert').hide();
                    }
                }
                else {
                    console.log(sFromDate + " : " + sToDate);
                    console.log("From date must be smaller than To date")
                }
            }
            else {
                console.log("Invalid: " + sFromDate + " : " + sToDate);
                console.log("invalid date format");
            }
        });
        return JSON.stringify(value);
    }
    else{
        return el.val();
    }
};

// check if email is in valid format
var validateEmail = function(el){

    el.closest('.form-group')
        .removeClass('has-error')
        .find('span.help-block')
        .remove();

    var value = el.val();
    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    if (regex.test(value)) {
        return true;
    } else {
        el.closest('.form-group')
            .addClass('has-error')
            .append('<span class="help-block">Invalid Email</span>');
        return false;
    }
};

// check if value in date field is in DD/MM/YYYY format
// and check if it is valid date and it is today or earlier
var validateDate = function(el){
    el.closest('.date-picker-group')
        .removeClass('has-error')
        .find('span.help-block')
        .remove();

    if (el.val().trim() == '') {
        el.val('');
        return true;
    }

    if (isValidDate(el.val())) {
        el.val(formatDate(stringToDate(el.val())));
        return true;
    }

    el.closest('.date-picker-group')
        .addClass('has-error')
        .append('<span class="help-block">Invalid Date</span>');

    return false;
};

// validates that a string is a valid date
var isValidDate = function(dateString) {
    if (dateString.trim() == '') {
        return true;
    }

    var dt = stringToDate(dateString);

    if (!isNaN(dt)) {
        var today = new Date();
        if (dt <= today && dt.getFullYear() > 1900) {
            return true;
        }
    }
    return false;
};

// take date string in DD/MM/YYYY format and return date object
var stringToDate = function(value){
    var regex = /(((0|1)[0-9]|2[0-9]|3[0-1]|[1-9])[\/-\\](0[1-9]|1[0-2]|[1-9])[\/-\\]((19|20)\d\d))$/;
    if (regex.test(value)) {
        var parts = value.split(/[\/\-\\]/);
        return new Date(parseInt(parts[2], 10), parseInt(parts[1], 10) - 1, parseInt(parts[0], 10));
    }
    // if the string isn't in DD/MM/YYYY format, try to parse it anyway
    return new Date(value);
};

// formats a date object as DD/MM/YYYY
var formatDate = function (dt) {
    var dd = dt.getDate();
    var mm = dt.getMonth() + 1; //January is 0!
    var yyyy = dt.getFullYear();
    if (dd < 10) {
        dd = '0' + dd;
    }
    if (mm < 10) {
        mm = '0' + mm;
    }
    return dd + '/' + mm + '/' + yyyy;
};

// check if separation date is less than one year from today
var checkSeparationDateLessThanYear = function(separationDate){
    // get separation date
    var date = stringToDate(separationDate);
    // get a date for a year from today
    var yearFromToday = new Date();
    yearFromToday.setYear(yearFromToday.getFullYear()-1);
    // if separation date is less than one year, display message
    return (date > yearFromToday);
};