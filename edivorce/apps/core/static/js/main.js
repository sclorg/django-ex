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

    // Delete button will remove field and update user responses
    $(".btn-delete").on('click', function () {
        // store neighbour input text to trigger change event to update list after delete
        var neighbour = $(this).parent('div').prev().find("input:text");
        $(this).parent('div').remove();
        neighbour.triggerHandler('change');
    });

    // Configuration for datepicker
    $(".date-picker-group").datepicker({
        format: "dd/mm/yyyy",
        endDate: "today",
        autoclose: true
    });

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

// Expand More Information boxes
// TODO this is fragile and really just a place holder until the sidebar is revised
$("#more_information").click(function () {
    if ($(this).hasClass("active")) {
        $(this).removeClass("col-md-4 active");
        $(".container-wrapper .col-md-8").addClass("col-md-offset-2");
    } else {
        $(this).addClass("col-md-4 active");
        $(".container-wrapper .col-md-8").removeClass("col-md-offset-2");
    }
});