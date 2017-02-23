// Reveal sections as the form is loading
$('input:radio, input:checkbox').each(function() {
  if($(this).is(':checked')) {
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
    $(".other-textbox").on("click focus", function(){
       $(this).siblings(".radio_with_textbox").prop('checked', true);
    });

    $("input[type=radio], input[type=checkbox], input[type=text], .response-textarea, .response-dropdown").on("change", ajaxOnChange);

    // On step_03.html, update text when user enters separation date
    $("#separated_date").on("change", function(){
        $("#separation_date_span").text(" on " + $(this).val());
        // if separation date is less than one year, show alert message
        if (checkSeparationDateLessThanYear($(this).val())){
            $('#separation_date_alert').show();
        }
        else {
            $('#separation_date_alert').hide();
        }
    });
});

// Expand More Information boxes
// TODO this is fragile and really just a place holder until the sidebar is revised
$( "#more_information" ).click(function() {
    if($(this).hasClass("active")) {
        $(this).removeClass("col-md-4 active");
        $(".container-wrapper .col-md-8").addClass("col-md-offset-2");
    } else {
        $(this).addClass("col-md-4 active");
        $(".container-wrapper .col-md-8").removeClass("col-md-offset-2");
    }
});