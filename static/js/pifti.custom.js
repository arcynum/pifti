/**
 * pifti.custom.js
 */

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
    
    // Attach events to each thumbnail cover
    $("div.media_embed").each(function () {
        var $embed = $(this).data("embed");
        var $id = $(this).data("id");
        var $width = $(this).css("width");
        var $height = $(this).height();
        var $expand = true;
        var $url = "";

        // Generate sources
        switch ($embed) {
            case "YoutubeBackend":
                $url = "https://www.youtube.com/embed/" + $id + "?rel=0&autoplay=1";
                break;

            case "VimeoBackend":
                $url = 'https://player.vimeo.com/video/' + $id + '?autoplay=1';
                break;

            case "SoundCloudBackend":
                $expand = false;
                $url = "https://w.soundcloud.com/player/" +
                    "?url=https://api.soundcloud.com/tracks/" + $id +
                    "&auto_play=true&hide_related=true&show_user=true&show_reposts=false&visual=true";
                break;

            default:
                console.log("Unidentified Backend: " + $embed);
                return false;
        }

        // Replace thumbnail cover with IFrame embed
        $(this).click(function () {
            $(this).replaceWith(generateEmbed($width, $height, $url, $expand));
        });
    });

});

// Build video embed DOM
function generateEmbed(width, height, url, expand) {
    var $aspect_ratio = height / 420;
    var $max_width = 1280;
    var $max_height = 720;
    var $container = $(document.createElement("div"));
        $container.attr("class", "media_embed");

    // Calculate aspect ratio from height
    if ($aspect_ratio >= 0.74) {
        $max_width = 960;
        $container.addClass("four_three"); // 4:3
    } else if ($aspect_ratio >= 0.55) {
        $container.addClass("sixteen_nine"); // 16:9
    } else {
        $max_width = 1680;
        $container.addClass("twentyone_nine"); // 21:9
    }

    // Build IFrame
    var $iframe = $(document.createElement("iframe"));
        $iframe.attr("height", "100%");
        $iframe.attr("width", "100%");
        $iframe.attr("src", url);
        $iframe.attr("frameborder", "no");
        $iframe.attr("scrolling", "no");
        $iframe.attr("webkitallowfullscreen", "");
        $iframe.attr("mozallowfullscreen", "");
        $iframe.attr("allowfullscreen", "");

    $container.append($iframe);

    // Attach expand button
    if (expand) {
        var $toggle = false;
        var $expand = $(document.createElement("div"));
            $expand.attr("class", "media_expand");
            $expand.addClass("expand");

        $expand.click(function () {
            if (!$toggle) {
                $(this).addClass("shrink").removeClass("expand");
                $(this).parent().css("width", $max_width + "px");
                $(this).parent().css("max-width", "calc(100% - 26px)");
                $(this).parent().css("max-height", $max_height + "px");
                $toggle = true;
            } else {
                $(this).addClass("expand").removeClass("shrink");
                $(this).parent().css("width", width);
                $(this).parent().css("max-width", width + "px");
                $(this).parent().css("max-height", height + "px");
                $toggle = false;
            }
        });

        $container.append($expand);
    }

    return $container;
}
