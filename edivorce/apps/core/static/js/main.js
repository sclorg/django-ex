// Reveal sections as the form is loading
$('input:radio, input:checkbox').each(function () {
    if ($(this).is(':checked')) {
        if ($(this).is(':visible')) {
            reveal($(this));
        }
        // apply css class to big round buttons
        if ($(this).parent().hasClass('btn-radio')) {
            $(this).parent().addClass('active');
        }
    }
});

$(window).load(function(){
    $('#questions_modal, #terms_modal').modal('show');
});

$(function () {
    $('[data-toggle="tooltip"]').tooltip({
        container: 'body',
        trigger: 'click',
        placement:'auto right'
    });

    // Only close Terms and Conditions when user check the I agree checkbox
    $('#terms_agree_button').on('click', function() {
        $('#terms_warning').remove();
        if ($('#terms_checkbox').is(':checked')) {
            $('#terms_modal').modal('hide');
        }
        else {
            // show warning box and warning message if user does not check the box and click aceept
            $('#terms_and_conditions').addClass('has-warning-box').append('<span id="terms_warning" class="help-block">Please check the box</span>');
        }
    });

    $('body').on('click', function (e) {
        $('[data-toggle=tooltip]').each(function () {
            // hide any open popovers when the anywhere else in the body is clicked
            if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.tooltip').has(e.target).length === 0) {
                if(!$(e.target).hasClass('keep-tooltip-open')) {
                    $(this).tooltip('hide');
                }
            }
        });
    });

    // when user click textbox beside radio button, check the associated radio button
    $(".other-textbox").on("click", function () {
        $(this).parent().find('.radio-with-other').prop('checked', true);
    });

    $("input[type=radio], input[type=checkbox], input[type=text], .response-textarea, .response-dropdown").on("change", ajaxOnChange);

    // If relationship is common law and they want spousal support, update spouse_support_act with hidden input field, spouse_support_act_common_law
    if ($("#spouse_support_act_common_law").length) {
        var el = $("#spouse_support_act_common_law");
        var question = el.prop('name');
        var value = getValue(el, question);
        ajaxCall(question, value);
    }

    // Add name button adds new input field for adding other name
    $("#btn_add_other_names").on('click', function () {
        $('#other_names_fields').append($('#other_names_group').children().clone(true));
    });

    $("#btn_add_reconciliation_periods").on('click', function () {
        $('#reconciliation_period_fields').append($('#reconciliation_period_group').children().clone());
        // add event lister for newly added from_date field, to_date field, delete button, and date picker
        $('#reconciliation_period_fields .reconciliation-from-date').last().on('change', ajaxOnChange);
        $('#reconciliation_period_fields .reconciliation-to-date').last().on('change', ajaxOnChange);
        $('#reconciliation_period_fields .btn-delete-period').last().on('click', {field_name: 'reconciliation_period_fields', button_name: 'btn_add_reconciliation_periods'}, deleteAddedField);
        date_picker('.date-pickers-group', true);
    });

    // Delete button will remove field and update user responses
    $(".btn-delete-name").on('click', {field_name: 'other_names_fields', button_name: 'btn_add_other_names'}, deleteAddedField);
    $(".btn-delete-period").on('click', {field_name: 'reconciliation_period_fields', button_name: 'btn_add_reconciliation_periods'}, deleteAddedField);

    // add date_picker
    date_picker('.date-picker-group', false);
    date_picker('.date-pickers-group', true);

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

    // For want which order page
    // If either Spousal support or Division of property and debts is not selected show alert message
    // if user still wants to proceed(click next again), let them proceed to next page
    $('#check_order_selected').on('click', function (e) {
        var showAlert = $(this).data('show_alert');
        var proceedNext = $(this).data('proceed');
        if (!showAlert) {
            $(".checkbox-group input:checkbox").not(":checked").each(function () {
                if ($(this).val() == 'Division of property and debts' || $(this).val() == 'Spousal support') {
                    showAlert = true;
                }
            });
        }
        if (showAlert && !proceedNext) {
            $('#unselected_orders_alert').show();
            e.preventDefault();
            $(this).data('proceed', true);
        }
    });

    // spinner
    $('a.spinner').on('click', function (e) {
        e.preventDefault();
        var href = $(this).attr('href');
        $('div#progress-overlay').show();
        $('div#progress-overlay-spinner').spin('large');
        setTimeout(function(){
            window.location.href = href;
        }, 0);
    });

    $('a.save-spinner').on('click', function (e) {
        var href = $('a.save-spinner').attr('href');
        e.preventDefault();
        $('div#progress-overlay').show();
        $('div#progress-overlay-spinner').spin('large');

        setTimeout(function(){
            window.location.href = href;
        }, 0);

    });

    // kills the spinner when the back button is pressed
    $(window).on('pageshow', function () {
        $('div#progress-overlay').hide();
        $('div#progress-overlay-spinner').spin(false);
    });

    $('.info-modal').on('click', function (e) {
        e.preventDefault();
        $('#info_modal').modal('show');
    })

});

// delete and added field and save the change
var deleteAddedField = function(e){
    var field = $('#' + e.data.field_name);
    var button = $('#' + e.data.button_name);
    $(this).parent('div').remove();

    // when there is only one field left, clear it instead of delete it
    if (field.find('input:text').length < 1){
        button.triggerHandler('click');
    }
    // update by trigger change event on one of the text field
    field.find('input:text').first().triggerHandler('change');
};

// Configuration for datepicker
var date_picker = function (selector, showOnFocus) {
    var startDate, endDate;
    if($(selector).data("allow-future-date")){
        startDate = "+1d";
        endDate = "+100y";
    }
    else {
        startDate = "-100y";
        endDate = "0d";
    }
    $(selector).datepicker({
        format: "dd/mm/yyyy",
        startDate: startDate,
        endDate: endDate,
        autoclose: true,
        todayHighlight: true,
        immediateUpdates: true,
        showOnFocus: showOnFocus,
        startView: 'decade',
        clearBtn: true
    }).on('dp.change', function(e) {
         $(this).find('input').trigger('change');
    }).on('show', function(e) {
         $(this).closest(selector).find('input').attr('readonly','readonly');
    }).on('hide', function(e) {
         $(this).closest(selector).find('input').removeAttr('readonly');
    }).on('clearDate', function (e) {
        var input = $(this).closest(selector).find('input');
        ajaxCall(input.attr('name'), '')
    });
};

// Expand More Information boxes
var moreInfo = $(".more_information-column");
var moreInfoLink = $(".more_information-link a");
var contentColumn = $(".col-flex.content-column");
$(".more_information-link a").click(function () {
    if ($(moreInfo).hasClass("off-canvas")) {
        $(moreInfo).removeClass("off-canvas").addClass("on-canvas");
        $(moreInfoLink).addClass("active");
        $(contentColumn).removeClass("margin-right").addClass("no-margin-right");
    } else {
        $(moreInfo).removeClass("on-canvas").addClass("off-canvas");
        $(moreInfoLink).removeClass("active");
        $(contentColumn).removeClass("no-margin-right").addClass("margin-right");
    }
});
$("a.more_information-close").click(function () {
    var moreInfo = $(".more_information-column");
    $(moreInfo).removeClass("on-canvas").addClass("off-canvas");
    $(moreInfoLink).removeClass("active");
    $(contentColumn).removeClass("no-margin-right").addClass("margin-right");
});

// Change border color on well when child has focus

$(".question-well").click(function () {
    $(".question-well").removeClass('hasFocus');
    $(this).addClass('hasFocus');
});

// disable collapse for links in data-toggle elements
$('.no-collapse').on('click', function (e) {
    e.stopPropagation();
});

