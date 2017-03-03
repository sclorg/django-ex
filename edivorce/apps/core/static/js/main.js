// Reveal sections as the form is loading
$('input:radio, input:checkbox').each(function () {
    if ($(this).is(':checked')) {
        reveal($(this));
        // apply css class to big round buttons
        if ($(this).parent().hasClass('btn-radio')) {
            $(this).parent().addClass('active');
        }
    }
});

$(function () {
    $('[data-toggle="tooltip"]').tooltip({trigger: 'click'});

    // when user click textbox beside radio button, check the associated radio button
    $(".other-textbox").on("click", function () {
        $(this).parents().find(".radio_with_textbox").prop('checked', true);
    });

    $("input[type=radio], input[type=checkbox], input[type=text], .response-textarea, .response-dropdown").on("change", ajaxOnChange);

    // Add name button adds new input field for adding other name
    $("#btn_add_other_names").on('click', function () {
        $('#other_names_fields').append($('#other_names_group').children().clone(true));
    });

    // TODO delete button is not working if they are added
    $("#btn_add_reconciliation_periods").on('click', function () {
        $('#reconciliation_period_fields').append($('#reconciliation_period_group').children().clone());
        $('#reconciliation_period_fields input:text').on('change', ajaxOnChange);
        // $('.btn-delete-period').on('click', deleteAddedField);
        date_picker();
    });

    // Delete button will remove field and update user responses
    $(".btn-delete-name").on('click', function () {
        $(this).parent('div').remove();

        // when there is only one field left, clear it instead of delete it
        if ($('#other_names_fields').find('input:text').length < 1){
            $("#btn_add_other_names").triggerHandler('click');
        }
        // update by trigger change event on one of the text field
        $('#other_names_fields').find('input:text').first().triggerHandler('change');

    });

    $(".btn-delete-period").on('click', function () {
        $(this).parent('div').remove();

        // when there is only one field left, clear it instead of delete it
        if ($('#reconciliation_period_fields').find('input:text').length < 1){
            $("#btn_add_reconciliation_periods").triggerHandler('click');
        }
        // update by trigger change event on one of the text field
        $('#reconciliation_period_fields').find('input:text').first().triggerHandler('change');

    });

    // add date_picker
    date_picker();

    // On step_03.html, update text when user enters separation date
    $("#separated_date").on("change", function () {
        $("#separation_date_span").text(" on " + $(this).val());
        // if separation date is less than one year, show alert message
        if (checkSeparationDateLessThanYear($(this).val())) {
            $('#separation_date_alert').show();
        }
        else {
            $('#separation_date_alert').hide();
        }
    });
});

// TODO make ajax call way too many times
var deleteAddedField = function(){
    console.log($(this));
    $(this).parent('div').remove();

    // when there is only one field left, clear it instead of delete it
    if ($('#reconciliation_period_fields').find('input:text').length < 1){
        $("#btn_add_reconciliation_periods").triggerHandler('click');
    }
    // update by trigger change event on one of the text field
    $('#reconciliation_period_fields').find('input:text').first().triggerHandler('change');
    console.log($('#reconciliation_period_fields').find('input:text').first());
};

// Configuration for datepicker
var date_picker = function () {
    $(".date-picker-group").datepicker({
        format: "dd/mm/yyyy",
        startDate: "-100y",
        endDate: "0d",
        autoclose: true,
        todayHighlight: true
    });
};

// Expand More Information boxes
$(".more_information-link a").click(function () {
    var moreInfo = $(".more_information-column");
    if ($(moreInfo).hasClass("hidden")) {
        $(moreInfo).removeClass("hidden");
    } else {
        $(moreInfo).addClass("hidden");
    }
});
$("a.more_information-close").click(function () {
    var moreInfo = $(".more_information-column");
    $(moreInfo).addClass("hidden");
});

// Change border color on well when child has focus

$(".question-well").click(function () {
    $(".question-well").removeClass('hasFocus');
    $(this).addClass('hasFocus');
});

// $('.question-well > *')
//     .focus(function() {
//         $(this).parent('.question-well').addClass('hasFocus');
//         console.log("FOCUS!");
//     })
//     .blur(function() {
//         $(this).parent('.question-well').removeClass('hasFocus');
//         console.log("NO FOCUS!");
//     });

