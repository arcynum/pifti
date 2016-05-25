/**
 * pifti.custom.js
 */

jQuery(document).ready(function($) {

    // Build a style element for dynamically generated CSS
    // Rules are injected using: stylesheet.injectRule(styleString, 0);
    var s = document.createElement('style'), styleSheet;
        s.id = "piftiCSS";
        s.title = "injectedCSS";
        document.head.appendChild(s);
        styleSheet = s.sheet;

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

            case "StreamableBackend":
                $url = 'https://streamable.com/e/' + $id + '?autoplay=1';
                break;
            
            case "GfycatBackend":
                $url = 'https://www.gfycat.com/ifr/' + $id;
                break;

            default:
                // Log backend and fail silently
                console.log("Unidentified Backend: " + $embed);
                return false;
        }

        // Replace thumbnail cover with IFrame embed
        $(this).click(function () {
            $(this).replaceWith(generateEmbed($width, $height, $url, $expand));
        });
    });

    // Build video embed DOM
    function generateEmbed(width, height, url, expand) {
        var $aspect_ratio = height / 420 * 100;
        var $max_width = 1280;
        var $max_height = 720;
        var $container = $(document.createElement("div"));
            $container.addClass("media_embed");

        // Restrict aspect ratio between 4:3 and ~21:9
        if ($aspect_ratio >= 75.0) {
            $max_width = 960;
            $container.addClass("four_three");
        } else if ($aspect_ratio <= 41.87) {
            $max_width = 1720;
            $container.addClass("twentyone_nine");
        } else {
            // Insert custom aspect ratio rule
            var $aspect_name = numberMap($aspect_ratio.toFixed(4));
            styleSheet.insertRule("div." + $aspect_name + ":after{padding-top:"
                + $aspect_ratio + "%;display:block;content:'';}", 0);
            $container.addClass($aspect_name);
            $max_width = Math.ceil($max_height * (100 / $aspect_ratio));
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
    
    // Map numbers to characters
    // Used for generating unique CSS rules from a calculated float value
    function numberMap(float_string) {
        return float_string.replace(/[0-9.%]/g, function (map) {
            return {
                '0': 'a', '1': 'b', '2': 'c', '3': 'd',
                '4': 'e', '5': 'f', '6': 'g', '7': 'h',
                '8': 'i', '9': 'j', '.': '', '%': ''
            }[map];
        });
    }

});
