jQuery(document).ready(function($) {
    $("#messages").fadeIn('slow');
    setTimeout(function() {
        $("#messages").fadeOut('slow');
    }, 6000);

    // Attach on click event to each hidden comments 'button'
    $("div.comments-expand").each(function() {
        $(this).click(function() {
            // Hide expand 'button'
            $(this).slideUp("slow");
            // Show hidden comments
            $(this).prev().slideDown("slow");
        })
    });
});