jQuery(document).ready(function($) {
    $("#messages").fadeIn('slow');
    setTimeout(function() {
        $("#messages").fadeOut('slow');
    }, 6000);
});