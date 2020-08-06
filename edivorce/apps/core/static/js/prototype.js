$(window).load(function () {
    function clearSignTogetherLocations() {
        $("#sign-in-person-both").prop('checked', false);
        $("#sign-virtual-both").prop('checked', false);
        $("#sign-virtual-both").trigger('change');
    }
    function clearSignSeparatelyLocations() {
        $("#sign-in-person-you").prop('checked', false);
        $("#sign-virtual-you").prop('checked', false);
        $("#sign-virtual-you").trigger('change');
        $("#sign-in-person-spouse").prop('checked', false);
        $("#sign-virtual-spouse").prop('checked', false);
        $("#sign-virtual-spouse").trigger('change');
    }
    function toggleSigningLocation() {
        if ($("#file-online").prop('checked')) {
            $("#signing-location").show();

            if ($("#sign-together").prop('checked')) {
                $("#signing-location-together").show();
                $("#signing-location-separately").hide();
                clearSignSeparatelyLocations();
            } else if ($("#sign-separately").prop('checked')) {
                clearSignTogetherLocations();
                $("#signing-location-together").hide();
                $("#signing-location-separately").show();
            }
        } else {
            $("#signing-location").hide();
            $("#signing-location-together").hide();
            $("#signing-location-separately").hide();
            clearSignSeparatelyLocations();
            clearSignTogetherLocations();
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
        } else {
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

    toggleSigningLocation();
    toggleSignVirtually();
    toggleFileInPerson();
});