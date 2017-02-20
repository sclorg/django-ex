// Show or Hide Information Section
// Using following data attributes:
// data-target_id: id of information section
// data-reveal_target: reveal target_id section if true
// data-related_id: id of information section which needed to be hide when target_id section is shown or vice versa
var reveal = function(el) {
    var id = '#' + el.data("target_id");
    var related_id = el.data("related_id");
    if (related_id != undefined) {
        related_id = '#' + related_id;
    }
    if (el.data("reveal_target") == true) {
        $(id).show();
        if (related_id != undefined){
            $(related_id).hide();
        }
    } else {
        $(id).hide();
        if (related_id != undefined){
            $(related_id).show();
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
        var otherTextBox = $(".other-textbox");
        otherTextBox.val('');
        ajaxCall(otherTextBox.prop('name'), '');
    }

    // Set focus to textbox for user convenience
    else if (el.is(".radio-with-other") && el.val() == 'Other'){
        $(".other-textbox").focus();
    }

    // when textbox is clicked, update associated radio button response with its value
    else if (el.is(".other-textbox")){
        var radioTextbox = $("#radio_with_textbox");
        ajaxCall(radioTextbox.prop('name'), radioTextbox.val());
    }
};

// Get value from various input fields
// If input is checkbox, get all checked items' value and separate them by ;
var getValue = function(el, question, value){
    // if checkbox, get list of values.
    if (el.is("input[type=checkbox]")){
        // special behaviour for question children_financial_support
        if (question == "children_financial_support"){
            childSupportCheckboxControl(el);
        }
        $(".checkbox-group").find("input[type=checkbox]:checked").each(function(){
            value += $(this).val() + '; ';
        });
        // to remove last space and semi-colon
        return value.slice(0, -2);
    }
    else{
        return el.val();
    }
};

// check if value in date field is in DD/MM/YYYY format
// and check if it is valid date and it is today or earlier
var validateDatePicker = function(value){
    var isValid = false;
    var regex = '[0-9]{2}[/][0-9]{2}[/][0-9]{4}';
    if (value.match(regex)){
        value = value.split('/');
        var d = parseInt(value[0], 10);
        var m = parseInt(value[1], 10);
        var y = parseInt(value[2], 10);
        var today = new Date();
        var date = new Date(y,m-1,d);
        if (date.getFullYear() == y && date.getMonth() + 1 == m && date.getDate() == d && date <= today) {
            isValid = true;
        }
    }
    return isValid;
};

// check if email is in valid format
var validateEmail = function(value){
    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return regex.test(value);
};