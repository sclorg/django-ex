// Reveal sections as the form is loading
var reveal_input_elements = function () {
    if ($(this).is(':checked')) {
        if ($(this).is(':visible')) {
            reveal($(this));
        }
        // apply css class to big round buttons
        if ($(this).parent().hasClass('btn-radio')) {
            $(this).parent().addClass('active');
        }
    }
};

$('input:radio, input:checkbox').each(reveal_input_elements);

$('input[type=number]').each(function() {
    if ($(this).is(':visible')) {
        reveal($(this));
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

    $('textarea').autogrow({onInitialize: true});

    // All elements tagged with the following sum related data attributes
    // will be added together and the result written to the html element
    // at the sum target id.
    //      data-sum=[true|false] - indicates input field should be included as an addend of a sum
    //      data-sum_class=[class name] - all elements with the same sum class identifier will be
    //                                      addends of the same sum.
    //      data-sum_target_id=[target id] - id of the html element where result of sum will be written
    $('[data-sum="true"]').on('change', sumFieldOnChange);

    // On page load make sure all sum totals are populated.
    $('[data-sum="true"]').each(sumFieldOnChange);

    // All elements tagged with the following mirror related data attributes
    // will have the value of the input fields mirror in other html elements.
    //      data-mirror=[true|false] - indicates when input field changes, the value of the input field should
    //                                  be mirror in one or more other elements.
    //      data-mirror_target=[selector] - selector for the target element to copy value into
    //      data-mirror_scale=[year_up|month_down] - year_up will multiply the number by 12 and month_down will divide the
    //                                                  the number by twelve.
    //      data-mirror_broadcast_change=[true|false] - after change the target element will trigger a change event so
    //                                                  so any listener attached to target element are notified that
    //                                                  contents have changed.
    $('[data-mirror="true"]').on('change', mirrorOnChange);
    $('[data-mirror_on_pressed="true"]').on('keyup', mirrorOnChange);


    // All of the input fields in the row will be saved as a single object
    // via an ajax call to the server.
    //      data-save_row=[true|false] - indicates whether all columns in row that contain an input field will
    //                                      be persisted to the server.
    $('[data-save_row="true"]').on('change', saveListControlRow);

    // All elements tagged with the following delta related data attributes
    // will have the delta between the two amounts calculated and the result written to
    // the html elements at the delta target selector. Will store the absolute value of the difference
    // of the terms.
    //      data-calc_delta=[true|false] - indicates input field should be included as term in the delta
    //      data-delta_term_selector=[selector] - all elements with the same delta class identifier will be
    //                                      addends of the delta.
    //      data-delta_target_selector=[selector] - all of the html elements where result of difference will be written
    $('[data-calc_delta="true"]').on('change', deltaFieldOnChange);
    $('[data-calc_delta="true"]').each(deltaFieldOnChange);


    // We want a way to dynamically calculate what proportion a given number is
    // relative to the sum of that number with another number. Our specific use
    // case is calculating the proportion of a given claimant's child support
    // payment relative to their spouse. We calculate these proportions based off
    // of each claimant's income.
    //      data-calc_percentage=[true|false]   - whether to compute amount between [0,100] inclusive.
    //      data-claimant_one_selector=[any jQuery input selector] - the input field that will contain claimant one
    //                                              income information. When the value in this input field changes the
    //                                              proportionate amounts will automatically get recalculated.
    //      data-claimant_two_selector=[any jQuery input selector] - the input field that will contain claimant two
    //                                              income information.
    $('[data-calc_percentage="true"]').each(function() {
        var fraction = function(part1, part2) {
            part1 = parseFloat(part1);
            part2 = parseFloat(part2);
            if (part1 + part2 === 0) {
                return 0;
            } else {
                return part1 / (part1 + part2);
            }
        };

        // Calculates the proportionate percentage of claimantOne to the sum of claimantOne
        // and claimantTwo. The result is a value between [0,100] inclusive.
        var calcPercentage = function(targetElement, claimantOne, claimantTwo) {
            targetElement.val(Math.round(fraction(claimantOne, claimantTwo) * 1000) / 10);
            targetElement.change();
        };

        var self = $(this);
        var claimantOneElement = $($(this).attr('data-claimant_one_selector'));
        var claimantTwoElement = $($(this).attr('data-claimant_two_selector'));

        self.on('change', ajaxOnChange);

        // Calculate and populate the field on initialization of page.
        calcPercentage(self, claimantOneElement.val(), claimantTwoElement.val());

        // Calculate and populate the fields whenever there is a change in the input
        // selectors.
        claimantOneElement.on('change', function() {
            calcPercentage(self, claimantOneElement.val(), claimantTwoElement.val());
        });
        claimantTwoElement.on('change', function() {
            calcPercentage(self, claimantOneElement.val(), claimantTwoElement.val());
        });
    });

    // Scale the value in the data-quantity element by the scale factor in the data-scale_factor
    // element, and store the result in the element with the data-scale attribute set.
    // Our specific use case is calculating the proportion of a given claimant's child support
    // payment relative to their spouse. We calculate these proportions based off of each claimant's income.
    //      data-scale=[true|false]   - whether to store scaled product in current element
    //      data-quantity=[any jQuery input selector] - the input field that will contain the factor that will be scaled.
    //      data-scale_factor=[any jQuery input selector] - the input field that will contain the scale that will be applied.
    $('[data-scale="true"]').each(function(){
        var self = $(this);
        var quantityElement = $($(this).attr('data-quantity'));
        var scaleFactorElement = $($(this).attr('data-scale_factor'));

        // Calculates the proportionate amount of claimantOne to the sum of claimantOne
        // and claimantTwo. The result is a value between [0,claimantOne] inclusive.
        var scale = function (targetElement, claimantAmount, proportionFactor) {
            var amount = parseFloat(proportionFactor) / 100 * parseFloat(claimantAmount);
            targetElement.val(amount.toFixed(2)).change();
        };

        scale(self, quantityElement.val(), scaleFactorElement.val());

        quantityElement.on('change', function() {
            scale(self, quantityElement.val(), scaleFactorElement.val());
        });

        scaleFactorElement.on('change', function() {
            scale(self, quantityElement.val(), scaleFactorElement.val());
        });
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
                if(!$(e.target).hasClass('keep-tooltip-open') && !$(this).hasClass('keep-tooltip-open')) {
                    $(this).tooltip('hide');
                }
            }
        });
    });

    // when user click textbox beside radio button, check the associated radio button
    $(".other-textbox").on("click", function () {
        $(this).parent().find('.radio-with-other').prop('checked', true);
    });

    $('input[type=number], input[type=radio], input[type=checkbox], input[type=text], .response-textarea, .response-dropdown').on('change', ajaxOnChange);

    // The designers want the dependent elements to be revealed as soon as the user completes input but before
    // they click on the next button. Using the keypress event with a small timeout to mimic an on change event
    // that does not require the current element to loose focus.
    $('input[name=number_children_over_19]').on('keypress', function() {
        var self = $(this);
        setTimeout(function(){ self.trigger('change');}, 50);
    });


    // If relationship is common law and they want spousal support, update spouse_support_act with hidden input field, spouse_support_act_common_law
    if ($("#spouse_support_act_common_law").length) {
        var el = $("#spouse_support_act_common_law");
        var question = el.prop('name');
        var value = getValue(el, question);
        ajaxCall(question, value);
    }

    // Add name button adds new input field for adding other name
    // Maximum of two other name fields allowed
    $("#btn_add_other_names").on('click', function () {
        if ($('#other_names_fields input[type=text]').length < 2) {
            $('#other_names_fields').append($('#other_names_group').children().clone(true));
        }

        showWarningOtherName();
    });

    // Show warning text when there are 2 other name fields
    var showWarningOtherName = function() {
        if ($('#other_names_fields input[type=text]').length >= 2) {
            $('#btn_add_other_names').hide();
            $('#other_name_warning_message').html("<p>Max 2 other names, please enter only the name variations to be shown on the order from the court</p>");
        }
    };

    // show warning message if other name field is already at its maximum number when the page rendered
    showWarningOtherName();

    var listControlGroups = [
        {
            table_selector: "#claimant_debts",
            add_button_selector: ".btn-add-debt",
            delete_button_selector: ".btn-delete-debt",
            input_field_selector: ".debt-input-field",
            clone_group_class: "debt-group",
            reveal_class: "debt-item-row"
        },
        {
            table_selector: "#claimant_expenses",
            add_button_selector: ".btn-add-expense",
            delete_button_selector: ".btn-delete-expense",
            input_field_selector: ".expense-input-field",
            clone_group_class: "expense-group",
            reveal_class: "expense-item-row"
        },
        {
            table_selector: "#supporting_non_dependents",
            add_button_selector: ".btn-add-supporting-non-dependent",
            delete_button_selector: ".btn-delete-supporting-non-dependent",
            input_field_selector: ".supporting-non-dependent-input-field",
            clone_group_class: "supporting-non-dependent-group",
            reveal_class: "supporting-non-dependent-item-row"
        },
        {
            table_selector: "#supporting_dependents",
            add_button_selector: ".btn-add-supporting-dependent",
            delete_button_selector: ".btn-delete-supporting-dependent",
            input_field_selector: ".supporting-dependent-input-field",
            clone_group_class: "supporting-dependent-group",
            reveal_class: "supporting-dependent-item-row"
        },
        {
            table_selector: "#supporting_disabled",
            add_button_selector: ".btn-add-supporting-disabled",
            delete_button_selector: ".btn-delete-supporting-disabled",
            input_field_selector: ".supporting-disabled-input-field",
            clone_group_class: "supporting-disabled-group",
            reveal_class: "supporting-disabled-item-row"
        },
        {
            table_selector: "#income_others",
            add_button_selector: ".btn-add-income-others",
            delete_button_selector: ".btn-delete-income-others",
            input_field_selector: ".income-others-input-field",
            clone_group_class: "income-others-group",
            reveal_class: "income-others-item-row"
        },
        {
            table_selector: "#claimant_children",
            add_button_selector: ".btn-add-child",
            delete_button_selector: ".btn-delete-child",
            input_field_selector: ".child-field",
            clone_group_class: "child-disabled-group",
            reveal_class: "child-item-row",
            customAction: function (settings, newElement) {
                $('.children-questions').show();
                enableChildrenFooterNav({page: 'edit'});

                // Want the second list row because that is before the newElement
                // was appended.
                var childCounter = $(settings.input_field_selector).last().closest('tr').prev().attr('data-counter');

                // Update the child id suffix so that now which row in table to update with these values.
                var updatedChildCounter = parseInt(childCounter, 10) + 1;
                newElement.closest('tr').attr('data-counter', updatedChildCounter);
                newElement.find(settings.input_field_selector + ', ' + settings.delete_button_selector).each(function () {
                    var fieldId = replaceSuffix($(this).attr('id'), updatedChildCounter);
                    $(this).attr('id', fieldId);
                });

                // Ensure that any previously select fields are cleared before we populate the input field
                // with the row selected in the table.
                $('[type=radio]').prop('checked', false);
                $('.children-input-block').each(function () {
                    resetChildrenInputBlock($(this), updatedChildCounter);
                });

                // When click the delete button for a row, make sure any handlers attached to the inputs
                // have been cleared.
                newElement.find(settings.delete_button_selector).on('click', function (e) {
                    e.preventDefault();
                    $('[type=radio]').prop('checked', false);
                    $('.children-input-block').each(function () {
                        resetChildrenInputBlock($(this), 'null');
                    });
                });

                // If the user clicks on the row, then should populate the input fields below the table
                // with the contents of the row.
                $('.children-list').hide();
                $('.fact-sheets').hide();

                initializeChildRowControls(newElement);
            },
            customDeleteAction: function(){}
        }
    ];
    listControlGroups.forEach(registerTableRowAddRemoveHandlers);


    var evaluateFactSheetShowCriteria = function(childrenData) {
        var childWithBoth = 0;
        var childWithYou = 0;
        var childWithSpouse = 0;
        childrenData.forEach(function(child) {
            if (child.child_live_with === 'Lives with you' ) {
                childWithYou += 1;
            }
            if (child.child_live_with === 'Lives with spouse') {
                childWithSpouse +=1;
            }
            if (child.child_live_with === 'Lives with both') {
                childWithBoth += 1;
            }
        });

        // show fact sheet b
        if (childWithBoth) {
            $('#fact_sheet_b').show();
        } else {
            $('#fact_sheet_b').hide();
        }

        // show fact sheet c
        // When the claimants have indicated that they have more than one child, then show fact sheet c if each
        // claimant has sole custody of at least one of the children or if one claimant has sole custody of at least one
        // child and the both claimants have shared custody of the remaining children.
        if (childWithYou && (childWithSpouse || childWithBoth)) {
            $('#fact_sheet_c').show();
        } else if (childWithSpouse && (childWithYou || childWithBoth)) {
            $('#fact_sheet_c').show();
        } else {
            $('#fact_sheet_c').hide();
        }
    };

    var populateChildrenFactSheets = function() {
        var childrenData = [];
        var element = $('#claimant_children');

        if (element.is('table')) {
            // The hidden row is the first now so make sure to skip it.
            element.find('tbody:first').find('tr:gt(0)').each(function () {
                var childData = {};
                $(this).find('.child-field').each(function () {
                    childData[$(this).attr('data-target-form-field')] = $(this).text();
                });

                childrenData.push(childData);
            });
        } else if (element.is('div')) {
            childrenData = JSON.parse(element.text());
        }

        evaluateFactSheetShowCriteria(childrenData);
    };


    var returnToParent = function(options) {
        $('.children-questions').hide();
        $('.children-list').show();
        enableChildrenFooterNav({page:'review'});

        if (options !== undefined && options.persist) {
            var childrenData = [];
            // The hidden row is the first row so make sure to skip it.
            $('#claimant_children').find('tbody:first').find('tr:gt(0)').each(function () {
                var childData = {};
                $(this).find('.child-field').each(function () {
                    childData[$(this).attr('data-target-form-field')] = $(this).text();
                });
                childrenData.push(childData);
            });
            var jsonChildrenData = JSON.stringify(childrenData);
            ajaxCall('claimant_children', jsonChildrenData);
        }
        populateChildrenFactSheets();
    };

    initializeChildRowControls($('body'));

    $('#btn_save_child').on('click', function(e) {
        e.preventDefault();
        returnToParent({persist: true});
    });
    $('#btn_revert_child').on('click', function(e) {
        e.preventDefault();
        returnToParent({persist: false});
    });

    $('#claimant_children').each(function(){
        populateChildrenFactSheets();
    });

    // check who has sole custody
    $('input[name="__claimant_children"]').each(function() {
        var children = JSON.parse($(this).val());
        var youHaveSoleCustody = children.every(function(child){
            return child.child_live_with === 'Lives with you'
        });
        var spouseHasSoleCustody = children.every(function(child){
            return child.child_live_with === 'Lives with spouse'
        });

        if (youHaveSoleCustody || spouseHasSoleCustody) {
            $('#monthly_amount_question').show();
        } else {
            $('#monthly_amount_question').hide();
        }
    });

    var payorCallback = function() {
        var claimant = $(this).val();

        var toggleFactSheetTable = function(table_suffix, claimant_name_selector, hide) {
            $('#fact_sheet_f').show();
            if (hide) {
                $('#fact_sheet_f_table_' + table_suffix).hide();
            } else {
                var fact_sheet_table_element = $('#fact_sheet_f_table_' + table_suffix);
                fact_sheet_table_element.show();
                fact_sheet_table_element.find('input:radio, input:checkbox').each(reveal_input_elements);
            }

            if (claimant_name_selector) {
                $('#fact_sheet_f_payor_title_' + table_suffix).text($(claimant_name_selector).text());
            }
        };

        if (claimant === 'Myself (Claimant 1)' && parseFloat($('input[name="annual_gross_income"]').val()) > 150000) {
            toggleFactSheetTable('1', '#__name_you');
            toggleFactSheetTable('2', null, true)
        } else if (claimant === 'My Spouse (Claimant 2)' && parseFloat($('input[name="spouse_annual_gross_income"]').val()) > 150000) {
            toggleFactSheetTable('2', '#__name_spouse');
            toggleFactSheetTable('1', null, true)
        } else if (claimant === 'Both myself and my spouse') {
            if (parseFloat($('input[name="annual_gross_income"]').val()) > 150000) {
                toggleFactSheetTable('1', '#__name_you');
            }
            if (parseFloat($('input[name="spouse_annual_gross_income"]').val()) > 150000) {
                toggleFactSheetTable('2', '#__name_spouse');
            }
        } else {
            $('#fact_sheet_f').hide();
            $('#fact_sheet_f_table_1').hide();
            $('#fact_sheet_f_table_2').hide();
        }

        if (claimant === 'Myself (Claimant 1)') {
            $('.payor-placeholder').text($('#__name_you').text());
        } else if (claimant === 'My Spouse (Claimant 2)') {
            $('.payor-placeholder').text($('#__name_spouse').text());
        } else if (claimant === 'Both myself and my spouse') {
            $('.payor-placeholder').text($('#__name_you').text() + ' and ' + $('#__name_spouse').text());
        } else {
            $('.payor-placeholder').text('the payor');
        }
    };

    $('input[name="child_support_payor"]').on('click', payorCallback).filter(':checked').each(payorCallback);


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
    // DIV-529 Separate alert for child support
    $('input[name="want_which_orders"]').on('click', function() {
        if ($('.show-order-alert-input').not(':checked').length === 0 ) {
            $('#unselected_orders_alert').hide();
        }

        // If the user has clicked the next button once, then make
        if($('#check_order_selected').data('proceed') === true) {
            if ($('.show-order-alert-input').not(':checked').length > 0 ) {
                $('#unselected_orders_alert').show();
            }
        }
    });

    $('#check_order_selected').on('click', function (e) {
        var showAlert = $(this).data('show_alert');
        var childSupport = $('input[data-target_id=child_support_alert]').prop('checked');
        var eligible = false;
        if (!childSupport) {
          var children = $('#unselected_child_support_alert').data('children-of-marriage');
          var under19 = $('#unselected_child_support_alert').data('children-number-under-19');
          var over19 = $('#unselected_child_support_alert').data('children-number-over-19');
          var reasons = $('#unselected_child_support_alert').data('children-financial-support');
          reasons = (reasons || []).filter(function(el){ return el !== 'NO'; }).length > 0;
          eligible = children === 'YES' && (under19 > 0 || (over19 > 0 && reasons));
        }
        var proceedNext = $(this).data('proceed');
        var showPropertyAlert = false;
        var showSpousalAlert = false;
        if (!showAlert) {
            $(".checkbox-group input:checkbox").not(":checked").each(function () {
                if ($(this).val() === 'Division of property and debts') {
                    showPropertyAlert = true;
                    showAlert = true;
                }
                if ($(this).val() === 'Spousal support') {
                    showSpousalAlert = true;
                    showAlert = true;
                }
            });
        }
        if ((showAlert || (!childSupport && eligible)) && !proceedNext) {
            $('#unselected_orders_alert').show();
            if (showPropertyAlert) {
                $('#unselected_property_alert').show();
            }
            if (showSpousalAlert) {
                $('#unselected_spouse_alert').show();
            }
            if (!childSupport && eligible) {
                $('#unselected_child_support_alert').show();
            }
            e.preventDefault();
            $(this).data('proceed', true);
        }
    });

    // For Prequalification step 3
    // If there is invalid date on reconciliation period,
    // prevent user from navigate away from the page when user clicks next or back button, or use side navigation
    $('#btn_reconcilaition_back, #btn_reconcilaition_next, .progress-column > a').on('click', function(e){
        if ($('.invalid-date').is(':visible')) {
            e.preventDefault();
            $('.invalid-date').parent().siblings('.form-group').find('.reconciliation-from-date').focus();
        }
    });


    $('.money').on('change', function() {
        var value = parseFloat($(this).val());
        $(this).val(value.toFixed(2));
    });

    $('.positive-integer').on('keypress', function(e) {
        // keyCode [95-105] - number page
        // keyCode [48-57] - 0-9
        // keyCode [8] - backspace
        // keyCode [37-40] - directional arrows
        if (!((e.which > 95 && e.which < 106) || (e.which > 47 && e.which < 58) || e.which === 8 || (e.keyCode > 36 && e.keyCode < 41))) {
            e.preventDefault();
        }
    });
    $('.positive-float').on('keypress', function(e) {
        // keyCode [95-105] - number page
        // keyCode [48-57] - 0-9
        // keyCode [8] - backspace
        // keyCode [37-40] - directional arrows
        if (!((e.which > 95 && e.which < 106) || (e.which > 45 && e.which < 58) || e.which === 8 || (e.keyCode > 36 && e.keyCode < 41))) {
            e.preventDefault();
        }
    });

    $('.fact-sheet-input').on('focus', function() {
        $(this).closest('td').addClass('table-cell-active');
    }).on('focusout', function() {
        $(this).closest('td').removeClass('table-cell-active');
    });

    // spinner
    // $('a.spinner').on('click', function (e) {
    //     e.preventDefault();
    //     var href = $(this).attr('href');
    //     $('div#progress-overlay').show();
    //     $('div#progress-overlay-spinner').spin('large');
    //     setTimeout(function(){
    //         window.location.href = href;
    //     }, 1);
    // });

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
    });

    $('.confirm-link').on('click', function (e) {
      if (!confirm($(e.target).data('message'))) {
        e.preventDefault();
      }
    });

    $('.previous-page').on('click', function(e) {
      e.preventDefault();
      window.history.back();
    });
});


// Options to enable/disable edit and delete controls from
// each child now.  Also, options to show appropriate tooltips
// for each control.
var initializeChildRowControls = function(element) {
    element.find('.btn-edit-child').on('click', function() {
        // Mimic what would happen if the parent row would be clicked.
        // this should initiate a transition to another screen where the
        // child details will be shown.
        $(this).closest('tr').find('.child-item-cell').first().click();
    }).hover(function() {
        $(this).tooltip({
            placement:'auto right',
            title: 'Edit details'
        });
        $(this).tooltip('show');
    }, function() {
        $(this).tooltip('hide');
    });
    element.find('.btn-delete-child').hover(function() {
        $(this).tooltip({
            placement:'auto right',
            title: 'Delete Child'
        });
        $(this).tooltip('show');
    }, function() {
        $(this).tooltip('hide');
    });
    element.find('.child-item-cell')
        .on('click', function() {
            if ($(this).hasClass('fact-sheet-button'))
                return;
            populateChildInputFields($(this).parent('tr'));
        });

    element.find('#delete_child_modal').on('show.bs.modal', function(event) {
        $('#delete_child_id').text(event.relatedTarget.id);
    });
    element.find('#confirm_delete_child').on('click', function() {
        var deleteButtonId = $('#delete_child_id').text();
        deleteChildData(undefined, $('#' + deleteButtonId));
        $('#delete_child_modal').modal('hide');
    });

    element.find('#cancel_delete_child').on('click', function() {
        $('#delete_child_modal').modal('hide');
    });
};

var populateChildInputFields = function(element) {
    $('.children-questions').show();
    $('.children-list').hide();
    $('.fact-sheets').hide();
    enableChildrenFooterNav({page:'edit'});

    $('[type=radio]').prop('checked', false);

    var activeChildRow = element.attr('data-counter');
    element.find('.child-field').each(function() {
        var fieldName = $(this).attr('data-target-form-field');
        var targetInput = $("input[name='" +fieldName + "']");
        if (targetInput.length === 0) {
            targetInput = $("textarea[name='" +fieldName + "']");
        }

        var mirrorTargetId = replaceSuffix(targetInput.attr('data-mirror_target'), activeChildRow);
        targetInput.attr('data-mirror_target', mirrorTargetId);

        if (targetInput.prop('type') === 'text' || targetInput.prop('type') === 'textarea') {
            targetInput.val($(this).text());
            targetInput.show();
        } else if (targetInput.prop('type') === 'radio') {
            targetInput.filter("[value='" + $(this).text() + "']").prop('checked', true);
        }
    });
};

var deleteChildData = function(settings, element) {
    $('[type=radio]').prop('checked', false);
    $('.children-input-block').each(function() {
        resetChildrenInputBlock($(this), 'null');
    });
    $('.children-questions').hide();
    deleteAddedTableRow(element);
    $('#btn_save_child').trigger('click');
};

var enableChildrenFooterNav = function(page) {
    if (page.page === 'edit') {
        $('#children_review_buttons').hide();
        $('#child_edit_buttons').show();
    } else if (page.page === 'review') {
        $('#children_review_buttons').show();
        $('#child_edit_buttons').hide();
    }
    window.scrollTo(0, 0);
};

var resetChildrenInputBlock = function(element, childCounter) {
    if (element.prop('type') === 'text' || element.prop('type') === 'textarea') {
        element.val('');
    }

    element.find('[data-mirror="true"]').off('change');
    element.find('[data-mirror="true"]').on('change', mirrorOnChange);

    var mirrorTargetId = replaceSuffix(element.attr('data-mirror_target'), childCounter);
    element.attr('data-mirror_target', mirrorTargetId);
};

var saveListControlRow = function(tableId) {
    var payload = [];
    var saveSelector = $(this).attr('data-save_select');

    var saveKey = null;
    var tableRows = null;

    if (!tableId.hasOwnProperty('originalEvent')) {
        saveKey = tableId;
        tableRows = $('#'+tableId).find('tbody:first').find('tr:gt(0)');
    } else {
        saveKey = $(this).closest('table').prop('id');
        tableRows = $(this).closest('tbody').find('tr:gt(0)');
    }

    tableRows.each(function() {
        var item = {};
        $(this).find(saveSelector).each(function() {
            item[$(this).prop('name')] = $(this).val();
        });
        payload.push(item);
    });

    var jsonPayload = JSON.stringify(payload);
    ajaxCall(saveKey, jsonPayload);
};



var replaceSuffix = function(str, suffix) {
    if (str !== undefined && str.lastIndexOf('_') !== -1) {
        str = str.substr(0, str.lastIndexOf('_'));
        str += '_' + suffix;
    }
    return str;
};

// All elements tagged with the following mirror related data attributes
// will have the value of the input fields mirror in other html elements.
//      data-mirror=[true|false] - indicates when input field changes, the value of the input field should
//                                  be mirror in one or more other elements.
//      data-mirror_target=[selector] - selector for the target element to copy value into
//      data-mirror_scale=[year_up|month_down] - year_up will multiply the number by 12 and month_down will divide the
//                                                  the number by twelve.
//      data-mirror_broadcast_change=[true|false] - after change the target element will trigger a change event so
//                                                  so any listener attached to target element are notified that
//                                                  contents have changed.
var mirrorOnChange = function(e) {
    // Don't mirror the change if the keypressed was tab. This is to prevent unnecessary calculations that may result
    // in some fields changing because scaling up to annual produces a slightly different result, due to rounding, than
    // scaling down.
    if (e.which === 9) {
        return;
    }
    var target_select = $(this).attr("data-mirror_target");
    var scale_factor_identifier = $(this).attr("data-mirror_scale");
    var broadcast_change = $(this).attr("data-mirror_broadcast_change");
    var target_element = null;
    var source_value = $(this).val();

    if (target_select !== undefined) {
        target_element = $(target_select);

        if (scale_factor_identifier !== undefined) {
            var scaled_value = parseFloat(source_value);
            if (scaled_value !== 0) {
                if (scale_factor_identifier === "year_up") {
                    scaled_value *= 12;
                } else if (scale_factor_identifier === "month_down") {
                    scaled_value /= 12;
                }
                source_value = scaled_value.toFixed(2);
            }
        }
        if (target_element.is('div') || target_element.is('span')) {
            target_element.text(source_value);
        } else {
            target_element.val(source_value);
        }

        if (broadcast_change !== undefined && broadcast_change) {
            target_element.trigger("change");
        }
    }
};

// delete and added field and save the change
var deleteAddedField = function(e){
    var field = $('#' + e.data.field_name);
    var button = $('#' + e.data.button_name);
    $(this).parent('div').remove();

    //enable btn_add_other_names button
    if (button.prop('id') === "btn_add_other_names"){
        button.show();
        $('#other_name_warning_message').html("");
    }

    // when there is only one field left, clear it instead of delete it
    if (field.find('input:text').length < 1){
        button.triggerHandler('click');
    }
    // update by trigger change event on one of the text field
    field.find('input:text').first().triggerHandler('change');
};

var deleteAddedTableRow = function(element) {
    // If the element being removed contained the sum attribute, cache the addend
    // class and sum target id so that can remove the element then recalculate the
    // total with the remaining elements.
    var sumTargetElement = element.closest('tr').find('[data-sum="true"]');
    var sumClass = null;
    var sumTargetId = null;
    if (sumTargetElement !== undefined) {
        sumClass = sumTargetElement.attr('data-sum_class');
        sumTargetId = sumTargetElement.attr('data-sum_target_id');
    }

    var tableId = element.closest('table').prop('id');

    element.closest('tr').remove();
    if (sumClass && sumTargetId) {
        sumFields('.' + sumClass, '#' + sumTargetId);
    }

    // we want to save the list if we remove an item.
    var payload = [];
    var saveKey = tableId;
    var tableElement = $('#'+tableId);
    var tableRows = tableElement.find('tbody:first').find('tr:gt(0)');
    var saveSelector = tableElement.find('[data-save_select]:first').attr('data-save_select');

    tableRows.each(function() {
        var item = {};
        $(this).find(saveSelector).each(function() {
            var fieldKey = $(this).prop('name');

            // For some tables, the contents of the tables cells are div instead of input fields.
            // In that case, check if the data-target-form-field attribute is set, that will contain
            // the field names to be saved.
            if (fieldKey === undefined) {
                fieldKey = $(this).attr('data-target-form-field')
            }

            var fieldValue = $(this).val();
            if ($(this).is('div')) {
                fieldValue = $(this).text();
            }
            item[fieldKey] = fieldValue;
        });
        payload.push(item);
    });

    var jsonPayload = JSON.stringify(payload);
    ajaxCall(saveKey, jsonPayload);
};

var registerTableRowAddRemoveHandlers = function(settings) {
    var cleanUp = function(e) {
        e.preventDefault();
        if (settings.hasOwnProperty('customDeleteAction')) {
            settings.customDeleteAction(settings, $(this));
        } else {
            deleteAddedTableRow($(this));
        }
    };

    $(settings.delete_button_selector).on('click', cleanUp);
    $(settings.add_button_selector).on('click', function(e) {
        e.preventDefault();
        var newRow = $('.' + settings.clone_group_class).clone();
        newRow.show();
        newRow.removeClass(settings.clone_group_class);
        newRow.addClass(settings.reveal_class);
        newRow.find(settings.delete_button_selector).on('click', cleanUp);
        newRow.find(settings.input_field_selector)
            .on('change', ajaxOnChange)
            .on('focus', function() {
                $(this).closest('td').addClass('table-cell-active');
            })
            .on('focusout', function() {
                $(this).closest('td').removeClass('table-cell-active');
            });
        newRow.find('[data-sum="true"]').on('change', sumFieldOnChange);
        newRow.find('[data-save_row="true"]').on('change', saveListControlRow);
        newRow.find('textarea').autogrow({onInitialize: true});

        $(settings.table_selector).find('tbody:first').append(newRow);

        if (settings.hasOwnProperty('customAction')) {
            settings.customAction(settings, newRow);
        }
    });
};

var sumFieldOnChange = function() {
    var sumClass = $(this).attr('data-sum_class');
    var sumTargetId = $(this).attr('data-sum_target_id');
    sumFields('.' + sumClass, '#' + sumTargetId);
};

var sumFields = function(addendSelector, sumSelector) {
    var total = 0.0;
    $(addendSelector).each(function () {
        if ($(this).val() !== undefined && $(this).val().length !== 0) {
            total += parseFloat($(this).val());
        }
    });
    total = total.toFixed(2);
    if (addendSelector !== undefined) {
        if ($(sumSelector).is("p")) {
            $(sumSelector).text(total);
        }
        else {
            $(sumSelector).val(total).change();
        }
    }
};


var deltaFieldOnChange = function() {
    var deltaTermSelector = $(this).attr('data-delta_term_selector');
    var deltaTargetSelector = $(this).attr('data-delta_target_selector');

    var delta = 0;
    $(deltaTermSelector).each(function(){
        delta = Math.abs($(this).val() - delta);
    });
    $(deltaTargetSelector).each(function() {
       $(this).val(delta).change();
    });
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
        format: "M d, yyyy",
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

