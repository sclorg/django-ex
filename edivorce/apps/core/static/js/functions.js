// Show or Hide Information Section
// Using following data attributes:
// data-target_id: id of information section
// data-reveal_target: reveal target_id section if true
// data-related_id: id of information section which needed to be hide when target_id section is shown or vice versa
var reveal = function(el) {
    var id = '#' + el.data("target_id");
    var css_class = el.data("target_class");
    var related_id = el.data("related_id");
    var reveal_condition = el.data("reveal_condition");
    var should_reveal = true;

    if (reveal_condition !== undefined) {
        should_reveal = false;
        if (reveal_condition.startsWith(">=")) {
            should_reveal = el.val() >= parseInt(reveal_condition.slice(2), 10);
        } else if (reveal_condition.startsWith("<=")) {
            should_reveal = el.val() <= parseInt(reveal_condition.slice(2), 10);
        } else if (reveal_condition.startsWith("==")) {
            should_reveal = el.val() === parseInt(reveal_condition.slice(2), 10);
        } else if (reveal_condition.startsWith("<")) {
            should_reveal = el.val() < parseInt(reveal_condition.slice(1), 10);
        } else if (reveal_condition.startsWith(">")) {
            should_reveal = el.val() > parseInt(reveal_condition.slice(1), 10) ;
        }

        if (!should_reveal) {
            if (related_id !== undefined){
                $('#' + related_id).hide();
            }
            if (css_class !== undefined){
                $('.' + css_class).hide();
            }
        }
    }

    if (should_reveal) {
        showHideTargetId(el, id, related_id);
        showHideRevealClass(el, css_class);

        if (el.prop('name') === "provide_certificate_later" || el.prop('name') === "original_marriage_certificate") {
            if ($('input[name=provide_certificate_later]:checked').val() !== 'YES' && $('input[name=original_marriage_certificate]:checked').val() === 'NO') {
                $('#is_certificate_in_english').hide();
            }
            else {
                $('#is_certificate_in_english').show();
            }
        }
    }
};

// hide or show based on target id
var showHideTargetId = function(el, id, related_id) {
    if (el.data("reveal_target") === true && el.prop('checked')) {
        $(id).show();
        if (related_id !== undefined){
            $('#' + related_id).hide();
        }
        if (id === "#has_children"){
            reveal($("input[name=number_children_over_19]"));
        }

        // reveal nested question as well
        if (id ==="#marriage_certificate"){
            reveal($("input[name=provide_certificate_later]:checked"));
        }
    } else {
        $(id).hide();
        if (related_id !== undefined){
            $('#' + related_id).show();
        }

        var revealCheckboxes = [
            {
                matchIdSelector: "#annual_gross_income",
                radioSelector: "input[name=agree_to_child_support_amount]:checked"
            },
            {
                matchIdSelector: "#spouse_annual_gross_income",
                radioSelector: "input[name=spouse_agree_to_child_support_amount]:checked"
            }
        ];

        revealCheckboxes.forEach(function(option) {
           if (id === option.matchIdSelector) {
               reveal($(option.radioSelector));
           }
        });
    }
};

// Controls show or hiding a target css class
var showHideRevealClass = function(el, target_css_class) {
    if (el.data("reveal_class") === false) {
        if (target_css_class !== undefined){
            $('.' + target_css_class).hide();
        }
    } else {
        if (target_css_class !== undefined){
            $('.' + target_css_class).show();
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
    if ($(".checkbox-group").find("input[type=checkbox]:checked").length === 0){
        el.prop('checked', true);
    }
    else {
        if (el.val() === "NO") {
            $("input[name=" + boxName + "]").each(function () {
                if ($(this).val() !== "NO") {
                    $(this).prop('checked', false);
                }
            });
        }
        else {
            $("input[name=" + boxName + "]").each(function () {
                if ($(this).val() === "NO") {
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
    if (el.is(".radio-with-other") && el.val() !== 'Other'){
        var otherTextBox = el.closest('div.radio').parent().find(".other-textbox");
        otherTextBox.val('');
        ajaxCall(otherTextBox.prop('name'), '');
    }

    // Set focus to textbox for user convenience
    else if (el.is(".radio-with-other") && el.val() === 'Other'){

        el.siblings($(".other-textbox")).focus();
    }

    // when textbox is clicked, update associated radio button response with its value
    else if (el.is(".other-textbox")){
        var radioTextbox = el.parent().parent().find(".radio-with-other");
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
        if (question === "children_financial_support"){
            childSupportCheckboxControl(el);
        }
        el.parents(".checkbox-group").find("input[type=checkbox]:checked").each(function(){
            value.push($(this).val());
        });
        // to remove last space and semi-colon
        return JSON.stringify(value);
    }
    // for adding other_name fields, create list of [aliasType, alias]
    else if (question === "other_name_you" || question === "other_name_spouse"){
        var aliasType = "also known as";
        $('#other_names_fields').find("input[type=text]").each(function () {
            // as per request, alias type will always be also known as for now
            // aliasType = $(this).val() === '' ? '' : $(this).siblings(".alias-type").val();
            value.push([aliasType, $(this).val()]);
        });
        return JSON.stringify(value);
    }
    // for adding reconciliation_period fields, create list of [sFromDate, sToDate] and
    // check if sFromDate is earlier than sToDate
    else if (question === "reconciliation_period"){
        var sToDate, sFromDate, dToDate, dFromDate;
        var hideAlert = true;
        $('#reconciliation_period_fields').find(".reconciliation-from-date").each(function () {
            sToDate = $(this).closest('div').next('div').find(".reconciliation-to-date").val();
            sFromDate = $(this).val();
            // check if both date is in valid format and all
            if (sToDate !== '' && sFromDate !== '' && isValidDate(sToDate) && isValidDate(sFromDate))
            {
                // clear previous errors
                $(this).closest('.form-inline').find('.date')
                    .removeClass('has-error');
                $(this).closest('.form-inline').find('span.help-block')
                    .remove();

                dToDate = stringToDate(sToDate);
                dFromDate = stringToDate(sFromDate);
                if (dFromDate < dToDate){
                    // check if date overlaps with other dates
                    if(!checkDateOverlap(value, dFromDate, dToDate)) {
                        value.push([sFromDate, sToDate]);
                        // show alert message if reconciliation period is greater than 90 days
                        if (dToDate.setDate(dToDate.getDate() - 90) > dFromDate) {
                            $('#reconciliation_90_days_alert').show();
                            hideAlert = false;
                        }
                        if (hideAlert) {
                            $('#reconciliation_90_days_alert').hide();
                        }
                    }
                    else {
                        $(this).closest('.form-inline').find('.date')
                        .addClass('has-error');
                        $(this).closest('.form-inline').find('.form-warning')
                            .append('<span class="help-block invalid-date">You have entered date periods that overlap, please check your dates and enter each period of time separately.</span>');
                    }
                }
                else {
                    $(this).closest('.form-inline').find('.date')
                        .addClass('has-error');
                    $(this).closest('.form-inline').find('.form-warning')
                            .append('<span class="help-block invalid-date">You have entered an end date (To:) that is earlier than the start date (From:), please check your dates and try again.</span>');
                }
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
    el.closest('.date')
        .removeClass('has-error')
        .find('span.help-block')
        .remove();

    if (el.val().trim() === '') {
        el.val('');
        return true;
    }

    var isFuture = el.is('.date-picker-future');
    if (isValidDate(el.val(), isFuture)) {
        el.val(formatDate(stringToDate(el.val())));
        return true;
    }

    el.closest('.date')
        .addClass('has-error')
        .append('<span class="help-block">Invalid Date</span>');

    return false;
};

// validates that a string is a valid date
var isValidDate = function(dateString, isFuture) {
    if (dateString.trim() === '') {
        return true;
    }

    var dt = stringToDate(dateString);

    if (!isNaN(dt)) {
        var today = new Date();
        if (isFuture && dt >= today && dt.getFullYear() <= today.getFullYear() + 100) {
            return true;
        }
        else if (!isFuture && dt <= today && dt.getFullYear() > 1900) {
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

// Check if new date overlaps with existing dates
var checkDateOverlap = function(dates, newFromDate, newToDate){
    if (dates.length === 0) {
        return false;
    }
    var isOverlap = true;
    var oldFromDate;
    var oldToDate;
    // No overlap when new From date is later than old To date
    // Or if new From date is earlier than old To date, and new To date is earlier than old From date.
    dates.forEach(function(date){
        oldFromDate = stringToDate(date[0]);
        oldToDate = stringToDate(date[1]);
        if(newFromDate > oldToDate) {
            isOverlap = false;
        }
        else {
            isOverlap = !(newToDate < oldFromDate);
        }
    });

    return isOverlap;
};