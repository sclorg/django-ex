// Internet Explorer 11 implementation of String does not have the startsWith function
// so manually add it to prevent an error on load.
if (!String.prototype.startsWith) {
    String.prototype.startsWith = function(searchString, position){
      position = position || 0;
      return this.substr(position, searchString.length) === searchString;
  };
}

// Internet Explorer 11 implementation does not have the replaceWith function
// so manually add polyfill version from MDN docs.
function ReplaceWithPolyfill() {
    'use-strict'; // For safari, and IE > 10
    var parent = this.parentNode, i = arguments.length, currentNode;
    if (!parent) return;
    if (!i) // if there are no arguments
        parent.removeChild(this);
    while (i--) { // i-- decrements i and returns the value of i before the decrement
        currentNode = arguments[i];
        if (typeof currentNode !== 'object'){
        currentNode = this.ownerDocument.createTextNode(currentNode);
        } else if (currentNode.parentNode){
        currentNode.parentNode.removeChild(currentNode);
        }
        // the value of "i" below is after the decrement
        if (!i) // if currentNode is the first argument (currentNode === arguments[0])
        parent.replaceChild(currentNode, this);
        else // if currentNode isn't the first
        parent.insertBefore(this.previousSibling, currentNode);
    }
}
if (!Element.prototype.replaceWith)
    Element.prototype.replaceWith = ReplaceWithPolyfill;
if (!CharacterData.prototype.replaceWith)
    CharacterData.prototype.replaceWith = ReplaceWithPolyfill;
if (!DocumentType.prototype.replaceWith)
    DocumentType.prototype.replaceWith = ReplaceWithPolyfill;

// Show or Hide Information Section
// Using following data attributes:
// data-target_id: id of information section
// data-reveal_target: reveal target_id section if true
// data-related_id: id of information section which needed to be hide when target_id section is shown or vice versa
// data-reveal_control_group: the selector for checkbox items that all behave as one group.  As long as one of them
//                          is checked, the target_id or target_class will be shown.  Otherwise
//                          if they are all unchecked, the target_id will be hidden.
var reveal = function(el) {
    var id = '#' + el.data("target_id");
    var cssClass = el.data("target_class");
    var relatedId = el.data("related_id");
    var revealCondition = el.data("reveal_condition");
    var invertTarget = el.data("invert_target");
    var revealControlGroup = el.data("reveal_control_group");

    var shouldReveal = true;

    if (revealCondition !== undefined) {
        shouldReveal = false;
        if (revealCondition.startsWith(">=")) {
            shouldReveal = el.val() >= parseFloat(revealCondition.slice(2));
        } else if (revealCondition.startsWith("<=")) {
            shouldReveal = el.val() <= parseFloat(revealCondition.slice(2));
        } else if (revealCondition.startsWith("==")) {
            shouldReveal = el.val() === parseFloat(revealCondition.slice(2));
        } else if (revealCondition.startsWith("<")) {
            shouldReveal = el.val() < parseFloat(revealCondition.slice(1));
        } else if (revealCondition.startsWith(">")) {
            shouldReveal = el.val() > parseFloat(revealCondition.slice(1));
        }

        if (!shouldReveal) {
            if (relatedId !== undefined) {
                $('#' + relatedId).hide();
            }
            if (cssClass !== undefined) {
                $('.' + cssClass).hide();
            }
            if (invertTarget !== undefined) {
                $(invertTarget).show();
            }
        }
    } else if (invertTarget !== undefined) {
        if ((el.is(':checkbox') || el.is(':radio')) && el.data("reveal_target")) {
            if (el.prop('checked')) {
                $(invertTarget).hide();
            } else {
                $(invertTarget).show();
            }
        } else {
            if (el.data("reveal_target")) {
                $(invertTarget).hide();
            } else {
                $(invertTarget).show();
            }
        }
    }

    if (shouldReveal) {
        showHideTargetId(el, id, relatedId, revealControlGroup);
        showHideRevealClass(el, cssClass);

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
var showHideTargetId = function(el, id, relatedId, revealControlGroup) {
    if (el.data("reveal_target") === true && el.prop('checked')) {
        $(id).show();
        if (relatedId !== undefined) {
            $('#' + relatedId).hide();
        }
        // Special case of hide child support description.
        if (id === "#child_support_in_order_detail") {
            $("#child_support_description").hide();
        }

        // reveal nested question as well
        if (id === "#marriage_certificate") {
            reveal($("input[name=provide_certificate_later]:checked"));
        }
    } else if (revealControlGroup !== undefined) {
        if ($(revealControlGroup).is(':checked').length === 0) {
            $(id).hide();
            if (relatedId !== undefined){
                $('#' + relatedId).show();
            }
        }
    } else {
        $(id).hide();

        // This is the bit of a hack/workaround but so far this is the only case
        // where we have a none nested related questions.  When the first
        // question is hidden, all elements in the force_hide group should also
        // be hidden.
        if (el.data("reveal_force_hide_group")) {
            $(el.data("reveal_force_hide_group")).hide();
            $(el.data("reveal_force_hide_group")).find(':radio').prop('checked', false);
        }

        // Special case of show child support description.
        if (id === "#child_support_in_order_detail") {
            $("#child_support_description").show();
        }

        if (relatedId !== undefined){
            $('#' + relatedId).show();
        }
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
};

// Controls show or hiding a target css class
var showHideRevealClass = function(el, targetCssClass) {
    if (el.data("reveal_class") === false) {
        if (targetCssClass !== undefined){
            $('.' + targetCssClass).hide();
        }
    } else {
        if (targetCssClass !== undefined){
            $('.' + targetCssClass).show();
            // This is to handle special case where multiple reveal options applied.
            if (targetCssClass === 'support-amount-match') {
                if ($("input[name=claimants_agree_to_child_support_amount]:checked").val() === 'YES') {
                    $('#what_special_provisions').hide();
                }
            }
        }
    }
};

// Controls Checkbox behaviour for a checkbox group.
// If a checkbox with the data-checkbox_radio_state_set=false is checked, un-check all checkboxes with
// data-checkbox_radio_state_set=true.
// If a checkbox with the data-checkbox_radio_state_set=true is checked, un-check all checkboxes with
// data-checkbox_radio_state_set=false.
// Once a checkbox is checked, at least one box will always be checked.
//      data-checkbox_radio=[true|false] - specifies which check boxes are part of of checkbox radio control
//      data-checkbox_radio_state_set=[true|false] - specifies whether part of the negative or positive checkbox
//                                                  radio state.  When an check box in the negative state is checked
//                                                  all checkboxes in the opposite state will be unchecked. Visa versa.
var checkboxRadioControl = function(el) {
    var boxName = el.prop("name");
    if (el.closest('.checkbox-group').find("input[type=checkbox]:checked").length === 0){
        el.prop('checked', true);
    } else {
        if (el.attr('data-checkbox_radio_state_set') === "false") {
            $("input[name=" + boxName + "]").filter('[data-checkbox_radio_state_set="true"]').each(function () {
                $(this).prop('checked', false);
            });
        } else {
            $("input[name=" + boxName + "]").filter('[data-checkbox_radio_state_set="false"]').each(function () {
                $(this).prop('checked', false);
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
        // Special case for child_support_in_order question which has option to use value from Factsheet C.
        // Change on radio button selection will save child support amount value as well.
        if (el.prop('name') === 'child_support_in_order') {
            var moneyTextBox = el.parent().find('.child-support-amount');
            ajaxCall(moneyTextBox.prop('name'), moneyTextBox.val());
        }
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
    if (el.is("input[type=checkbox]")) {
        if (el.is('[naked]')) {
          return el.is(':checked') ? 'true' : 'false';
        }

        if (el.attr('data-checkbox_radio') === "true") {
            checkboxRadioControl(el);
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
        $('#other_names_fields').find('.alias-field-group').each(function () {
            var lastName = $(this).find(".alias-last-name").val();
            var given1 = $(this).find(".alias-given-1").val();
            var given2 = $(this).find(".alias-given-2").val();
            var given3 = $(this).find(".alias-given-3").val();
            value.push([aliasType, lastName, given1, given2, given3]);
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
    } else if (el.is("input[type=radio]")) {
        if (el.prop('checked')) {
            return el.val();
        } else {
            return '';
        }
    } else {
        return el.val();
    }
};

var isEmailValid = function(el) {
    var value = el.val();
    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return regex.test(value);
}

// check if email is in valid format
var validateEmail = function(el){

    el.closest('.form-group')
        .removeClass('has-error')
        .find('span.help-block')
        .remove();

    if (!el.val() || isEmailValid(el)) {
        return true;
    } else {
        el.closest('.form-group')
            .addClass('has-error')
            .append('<span class="help-block">Invalid Email</span>');
        return false;
    }
};

var validateName = function(el){

    el.closest('.form-group')
    .removeClass('has-error')
    .find('span.help-block')
    .remove();

    var value = el.val();
    var hasDigit = /\d/;

    // check to make sure there are no digits in the string, 
    // because CEIS won't accept it
    if (hasDigit.test(value)){
        el.closest('.form-group')
        .addClass('has-error')
        .append('<span class="help-block">A name cannot have a number in it.</span>');
        return false;
    }

    return true;
};

var $DateFormat = 'M d, yyyy';
var MomentFormat = 'MMM D, YYYY';

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

    var date = new Date(el.val());
    var isFuture = el.is('.date-picker-future');
    if (isValidDate(el.val(), isFuture)) {
        el.val(moment(stringToDate(el.val())).format('MMM D, YYYY'));
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
