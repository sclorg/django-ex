$(window).load(function () {
    function setSignSeparatelyDefaults() {
        $("#sign-in-person-both").prop('checked', true).trigger('change');
        if ($("input:radio[name='signing_location_you']:checked").length === 0) {
            $("#sign-in-person-you").prop('checked', true).trigger('change');
        }
        if ($("input:radio[name='signing_location_spouse']:checked").length === 0) {
            $("#sign-in-person-spouse").prop('checked', true).trigger('change');
        }
    }

    function setSignTogetherDefaults() {
        $("#sign-in-person-you").prop('checked', true).trigger('change');
        $("#sign-in-person-spouse").prop('checked', true).trigger('change');
        if ($("input:radio[name='signing_location']:checked").length === 0) {
            $("#sign-in-person-both").prop('checked', true).trigger('change');
        }
    }

    function toggleSigningLocation() {
        if ($("#file-online").prop('checked')) {
            $("#signing-location").show();

            if ($("#sign-together").prop('checked')) {
                setSignTogetherDefaults();
                $("#signing-location-together").show();
                $("#signing-location-separately").hide();
            } else {
                setSignSeparatelyDefaults();
                $("#signing-location-together").hide();
                $("#signing-location-separately").show();
            }
        } else {
            $("#signing-location").hide();
            $("#signing-location-together").hide();
            $("#signing-location-separately").hide();
            setSignTogetherDefaults();
            setSignSeparatelyDefaults();
        }
    }

    function toggleSignVirtually() {
        var signVirtuallyBoth = $("#sign-virtual-both").prop('checked');
        var signVirtuallyYou = $("#sign-virtual-you").prop('checked');
        var signVirtuallySpouse = $("#sign-virtual-spouse").prop('checked');

        var needEmailYou = (signVirtuallyBoth || signVirtuallyYou) && $("#existing-email-you").val() === '';
        var needEmailSpouse = signVirtuallySpouse && $("#existing-email-spouse").val() === '';

        if (needEmailYou || needEmailSpouse) {
            $("#sign-virtually").show();
        } else {
            $("#sign-virtually").hide();
        }
        if (needEmailYou) {
            $("#email-you").show();
        } else {
            $("#email-you").hide();
            $("#email-you-input").removeClass('error');
        }
        if (needEmailSpouse) {
            $("#email-spouse").show();
        } else {
            $("#email-spouse").hide();
            $("#email-spouse-input").removeClass('error');
        }
        $('#unfilled-email-alert').hide();
    }

    function toggleFileInPerson() {
        if ($("#file-in-person").prop('checked')) {
            $("#sign-in-person").show();
            $("#signing-location").hide();
        } else if ($("#file-online").prop('checked')) {
            $("#sign-in-person").hide();
            $("#signing-location").show();
        }
    }

    $("#sign-separately, #sign-together, #file-online, #file-in-person").change(toggleSigningLocation);
    $("#sign-virtual-both, " +
        "#sign-in-person-both, " +
        "#sign-virtual-you, " +
        "#sign-in-person-you, " +
        "#sign-in-person-spouse, " +
        "#sign-virtual-spouse").change(toggleSignVirtually);
    $("#file-in-person, #file-online").change(toggleFileInPerson);

    function setDefaults() {
        if ($("input:radio[name='how_to_sign']:checked").length === 0) {
            $("#sign-together").prop('checked', true).trigger('change');
        }

        // If filing options are not visible, default to In-person
        if ($("input:radio[name='how_to_file']").length === 0) {
            ajaxCall('how_to_file', 'In-person');
        } else if ($("input:radio[name='how_to_file']:checked").length === 0) {
            $("#file-online").prop('checked', true).trigger('change');
        }
    }

    // Set signing and filing defaults if the signing option is on the page
    if ($("input:radio[name='how_to_sign']").length > 0) {
        setDefaults()
    }

    // Set filing location defaults if the filing option is on the page
    if ($("input:radio[name='how_to_file']").length > 0) {
        toggleSigningLocation();
        toggleSignVirtually();
        toggleFileInPerson();
    }

    $('#check-email-filled').on('click', function (e) {
        var yourEmailInput = $('#email-you-input');
        var yourEmailError = yourEmailInput.is(":visible") && !(yourEmailInput.val() && isEmailValid(yourEmailInput));
        var spouseEmailInput = $('#email-spouse-input');
        var spouseEmailError = spouseEmailInput.is(":visible") && !(spouseEmailInput.val() && isEmailValid(spouseEmailInput));
        if (yourEmailError || spouseEmailError) {
            $('#unfilled-email-alert').show();
            $('#error-email-you').toggle(yourEmailError)
            $('#error-email-spouse').toggle(spouseEmailError)
            yourEmailInput.toggleClass('error', yourEmailError);
            spouseEmailInput.toggleClass('error', spouseEmailError);
            e.preventDefault();
        } else {
            $('#unfilled-email-alert').hide();
        }
    });

    if ($('#court-registry-location').length > 0) {
        var city = $('#court-registry-city').text()
        var url = $(location).attr('origin') + window.sm_base_url + 'api/court_location/' + city + '/';
        $.ajax(url,
            {
                type: 'GET',
            }).success((response) => {
            var data = JSON.parse(response);
            $('#court-registry-address').text(data.address);
            $('#court-registry-postal-code').text(data.postal_code);
        }).error((response) => {
            $('#court-registry-address').html('<span class="error-text">No address found</span>');
            $('#court-registry-postal-code').html('<a href="https://www.bccourts.ca/supreme_court/court_locations_and_contacts.aspx">Look up address</a>');
        });
    }

});