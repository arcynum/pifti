/**
 * pifti.custom.js
 */

jQuery(document).ready(function($) {
    var p = 'https:';
    // Check for secure connection
    if (location.protocol != 'https:') { p = 'http:' }

    // Setup min/max environment variables for responsive embeds
    var minwidth = 420, minheight = 176, maxwidth = 420, maxheight = 315;

    // Build a style element to hold dynamically generated CSS
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
            // Begin generating media covers
            $(this).prev().find("div.media_embed").each(function () {
                generateCover($(this), p);
            });
            // Show hidden comments
            $(this).prev().slideDown("slow");
        })
    });
    
    // Attach events and create covers for each visible media embed
    $("div.media_embed:visible").each(function () {
        generateCover($(this), p);
    });

    // Generate responsive thumbnail cover for media embed
    function generateCover(obj, protocol) {
        var $embed = $(obj).data("embed"); // Backend name
        var $id = $(obj).data("id"); // Media code
        var $start = $(obj).data("start"); // Media start time in seconds
        var $width = minwidth; // Smallest responsive cover width in pixels
        var $height = minheight; // Smallest responsive cover height in pixels
        var $api = protocol; // Hosts oEmbed API, append to this variable
        var $base_url = protocol; // Video URL, append to this variable
        var $embed_url = protocol; // Iframe source URL or video source list
        var $thumb = undefined; // Thumbnail URL
        var $title = "Loading..."; // Media title
        var $author = "Anonymous"; // Media author
        var $player = "iframe"; // DOM embed type, <iframe> or <video>
        var $expand = true; // Expandable player

        if ($embed === undefined || $id === undefined) {
            console.log("Detected responsive embed has invalid embed and/or id data.");
            return false;
        } else if ($start === undefined) {
            $start = 0;
        }

        // Generate sources
        switch ($embed) {
            case "YoutubeBackend":
                $author = "Youtube";
                $api = 'https://www.youtube.com/oembed';
                $base_url += '//youtube.com/watch?v=' + $id;
                $embed_url += '//www.youtube.com/embed/' + $id
                    + '?rel=0&autoplay=1&start=' + $start;
                break;

            case "VimeoBackend":
                $author = "Vimeo";
                $api += '//vimeo.com/api/oembed.json';
                $base_url += '//vimeo.com/' + $id;
                $embed_url += '//player.vimeo.com/video/' + $id
                    + '?autoplay=1';
                break;

            case "SoundCloudBackend":
                $author = "Soundcloud";
                $api += '//soundcloud.com/oembed';
                // Check if we have the soundcloud track ID or author/track format
                if (/^\d+$/.test($id)) {
                    $base_url += '//api.soundcloud.com/tracks/' + $id;
                } else {
                    $base_url += "//soundcloud.com/" + $id;
                }
                $expand = false;
                $embed_url += '//w.soundcloud.com/player/'
                    + '?url=' + $base_url
                    + '&auto_play=true'
                    + '&hide_related=true&show_user=true'
                    + '&show_reposts=false&visual=true';
                break;

            case "StreamableBackend":
                $author = "Streamable";
                $api += '//api.streamable.com/oembed.json';
                $base_url += '//streamable.com/' + $id;
                $thumb = protocol + '//cdn.streamable.com/image/' + $id + '.jpg';
                $embed_url += '//streamable.com/e/' + $id
                    + '?autoplay=1&hd=1&t=' + $start;
                break;

            case "DailymotionBackend":
                $author = "Dailymotion";
                $api += '//www.dailymotion.com/services/oembed';
                $base_url += '//dailymotion.com/video/' + $id;
                $embed_url += '//www.dailymotion.com/embed/video/' + $id
                    + '?autoplay=true&endscreen-enable=false&quality=380'
                    + '&sharing-enable=false&start=' + $start;
                break;

            case "GfycatBackend":
                $author = "Gfycat";
                $api += '//api.gfycat.com/v1/oembed';
                $base_url += '//gfycat.com/' + $id;
                $thumb = protocol + '//thumbs.gfycat.com/' + $id + '-poster.jpg';
                $player = "video";
                $embed_url = [
                    protocol + '//giant.gfycat.com/' + $id + '.webm',
                    protocol + '//giant.gfycat.com/' + $id + '.mp4',
                    protocol + '//zippy.gfycat.com/' + $id + '.webm',
                    protocol + '//zippy.gfycat.com/' + $id + '.mp4'
                ];
                break;

            default:
                // Log backend and fail silently
                console.log("Unidentified Backend: " + $embed);
                return false;
        }

        $(obj).find("span.media_author").html($author);
        $(obj).find("span.media_title").html($title);

        // TODO: Fix preflight OPTIONS request for cross domains
        $.ajax({
            method: "GET",
            url: $api,
            crossDomain: true,
            headers: {
                //'Access-Control-Allow-Origin': '*',
                //'Access-Control-Max-Age': '30',
                //'Access-Control-Allow-Methods': 'GET,HEAD,OPTIONS',
                //'Access-Control-Allow-Headers': 'x-requested-with,content-type,origin
            },
            data: {
                url: $base_url,
                maxwidth: maxwidth, // Maximum embed width
                maxheight: maxheight, // Maximum embed height
                format: 'json'
            },
            success: function (data) {
                // Check for successful responses containing errors
                if (data['errorMessage'] != undefined) {
                    // Gfycat returns errorMessage upon failure
                    var error = jQuery.parseJSON(data['errorMessage']);
                    ajaxError(obj, $id, $base_url, error['code']);
                } else if (data['type'] === undefined) {
                    // Dailymotion does not always return data upon failure.
                    // `Type` is a required property for oEmbed compliance,
                    // thus it must exist within valid responses.
                    ajaxError(obj, $id, $base_url, "Invalid Video Url");
                } else {
                    if ($expand) {
                        $height = Math.max(data['height'], minheight);
                    }
                    if (data['width'] != undefined) {
                        $width = Math.max(data['width'], minwidth);
                    }
                    if (data['title'] != undefined) $title = data['title'];
                    if (data['author_name'] != undefined) $author = data['author_name'];

                    // Find better quality thumbnails for these backends
                    if ($thumb === undefined) {
                        var code = null;

                        switch ($embed) {
                            case "YoutubeBackend":
                                $thumb = data['thumbnail_url'];
                                break;

                            case "VimeoBackend":
                                $thumb = data['thumbnail_url'];

                                code = /\/\d+_/.exec($thumb);
                                if (code != null) {
                                    $thumb = protocol + "//i.vimeocdn.com/video"
                                        + code + $width + "x" + $height + ".jpg";
                                }
                                break;

                            case "SoundCloudBackend":
                                $thumb = data['thumbnail_url'];

                                // Ensure thumbnail url matches request protocol
                                $thumb = $thumb.replace(/^http:/i, protocol);
                                break;

                            case "DailymotionBackend":
                                $thumb = data['thumbnail_url'];

                                // Do not try and find larger PNG thumbnail
                                if (/\.png$/i.test($thumb)) { break }

                                code = /\/(\w+)\//.exec($thumb);
                                if (code != null) {
                                    // Different server for secure connection
                                    if (protocol === 'http:') {
                                        $thumb = protocol + "//s1.dmcdn.net/"
                                            + code[1] + ".jpg";
                                    } else {
                                        $thumb = protocol + "//s1-ssl.dmcdn.net/"
                                            + code[1] + ".jpg";
                                    }
                                }
                                break;

                            default:
                                $thumb = data['thumbnail_url'];
                                break;
                        }
                    }

                    $(obj).css("height", $height + "px");
                    $(obj).find("span.media_title").html($title);
                    $(obj).find("span.media_author").html($author);
                    $(obj).find("div.media_cover").css("background-image",
                        "url(" + $thumb + ")");

                    // When clicked replace thumbnail cover with IFrame embed
                    $(obj).click(function () {
                        $(this).replaceWith(generateEmbed($width, $height, $embed_url, $expand, $player));
                    });
                }
            },
            error: function (e) {
                // Data return failure
                ajaxError(obj, $id, $base_url, e.statusText)
            }
        });
    }

    // Build video embed DOM
    function generateEmbed(width, height, embed_url, expand, player) {
        var $aspect_ratio = height / width * 100; // Embed aspect ratio
        var $max_width = 1280; // Largest width for expanded embed
        var $max_height = 720; // Largest height for expanded embed
        var $re_webm = /(\.webm)$/; // Regex detect webm extension
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

        // Build player
        if (player === "video") {
            var $video = $(document.createElement("video"))
                .attr("height", "100%")
                .attr("width", "100%")
                .attr("preload", "none")
                .attr("autoplay", "")
                .attr("controls", "")
                .attr("loop", "");
            embed_url.forEach(function generateSource(source) {
                var $source = $(document.createElement("source"))
                    .attr("src", source);
                if ($re_webm.test(source)) {
                    $source.attr("type", "video/webm");
                } else {
                    $source.attr("type", "video/mp4");
                }
                $video.append($source);
            });
            $container.append($video);
        } else {
            var $iframe = $(document.createElement("iframe"))
                .attr("height", "100%")
                .attr("width", "100%")
                .attr("src", embed_url)
                .attr("frameborder", "no")
                .attr("scrolling", "no")
                .attr("webkitallowfullscreen", "")
                .attr("mozallowfullscreen", "")
                .attr("allowfullscreen", "");
            $container.append($iframe);
        }

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
                    $(this).parent().css("width", width + "px");
                    $(this).parent().css("max-width", maxwidth + "px");
                    $(this).parent().css("max-height", height + "px");
                    $toggle = false;
                }
            });

            $container.append($expand);
        }

        return $container;
    }

    function ajaxError(obj, id, base_url, error) {
        // Print error and minimize embed
        $(obj).find("span.media_title").html("Failed to load "
            + " ID <a href=" + base_url + ">" + id + "</a>: " + error);
        $(obj).find("div.play_button").remove();
        $(obj).css("height", 60 + "px");
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
