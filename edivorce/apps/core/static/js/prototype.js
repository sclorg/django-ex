$(window).load(function () {
    function setSignSeparatelyDefaults() {
        $("#sign-in-person-both").prop('checked', false);
        $("#sign-virtual-both").prop('checked', false);
        $("#sign-virtual-both").trigger('change');
        if ($("input:radio[name='signing_location_you']:checked").length === 0) {
            $("#sign-in-person-you").prop('checked', true).trigger('change');
        }
        if ($("input:radio[name='signing_location_spouse']:checked").length === 0) {
            $("#sign-in-person-spouse").prop('checked', true).trigger('change');
        }
    }

    function setSignTogetherDefaults() {
        $("#sign-in-person-you").prop('checked', false);
        $("#sign-virtual-you").prop('checked', false).trigger('change');
        $("#sign-in-person-spouse").prop('checked', false);
        $("#sign-virtual-spouse").prop('checked', false).trigger('change');
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
            } else if ($("#sign-separately").prop('checked')) {
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
        if ($("#sign-virtual-both").prop('checked') || $("#sign-virtual-you").prop('checked') || $("#sign-virtual-spouse").prop('checked')) {
            $("#sign-virtually").show();
        } else {
            $("#sign-virtually").hide();
        }
        if ($("#sign-virtual-both").prop('checked') || $("#sign-virtual-you").prop('checked')) {
            $("#email-you").show();
        } else {
            $("#email-you").hide();
        }
        if ($("#sign-virtual-spouse").prop('checked')) {
            $("#email-spouse").show();
        } else {
            $("#email-spouse").hide();
        }
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

    function selectDefaults() {
        if ($("input:radio[name='how_to_sign']:checked").length === 0) {
            $("#sign-together").prop('checked', true).trigger('change');
        }
        if ($("input:radio[name='how_to_file']:checked").length === 0) {
            $("#file-online").prop('checked', true).trigger('change');
        }
    }

    selectDefaults()

    $("#sign-separately, #sign-together, #file-online, #file-in-person").change(toggleSigningLocation);
    $("#sign-virtual-both, " +
        "#sign-in-person-both, " +
        "#sign-virtual-you, " +
        "#sign-in-person-you, " +
        "#sign-in-person-spouse, " +
        "#sign-virtual-spouse").change(toggleSignVirtually);
    $("#file-in-person, #file-online").change(toggleFileInPerson);

    toggleSigningLocation();
    toggleSignVirtually();
    toggleFileInPerson();
});