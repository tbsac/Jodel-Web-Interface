

$(function() {
    load_recent()
})

API_URL = "http://localhost:8080/"


function apicall(path, cb) {
    $.ajax({
        url: API_URL + path,
        cache: false,
        dataType: "json",
        error: function(xhr, status, error) {
            console.log("Error during request to " + path)
            console.log("Error: ", error, "Status: ", status)
        },
        success: function(data, text, xhr) {
            console.log("Response: ", data)
            if (data.error) {
                console.error("Error from server!")
                console.warn("Message:", data.error)
                console.warn("Errorcode:", data.errorcode)
            }
            cb(data)
        }

    })
}



function load_recent() {
    $("#navigator").html("Recent Posts");
    apicall("posts/recent/", function(posts) {
        render_posts(posts.posts)
    })
}


function render_posts(posts) {
    contents = ["", "", ""]


    var i = 0
    posts.forEach(function(post) {
        var content = ""
        add_class = post.image_url ? " image_post" : "";

        content += "<div class='post" + add_class + "' style='background-color: #" + post.color + "'>"
        
        if (post.image_url)
        {
            content += "<div class='image_cropper'><img src='http:" + post.image_url + "' /></div>"
        } else {
            content += "<p>" + post.message.replace(/\n/g, "<br />") + "</p>"
        }

        content += "<span class='vote_count'>" + post.vote_count + "</span>"
        content += "<span class='post_footer'>"

        content += "<span class='post_id'>" + post.post_id + "</span> "
        content += "<span class='comments_count'>" + (post.child_count || "Keine") + " Kommentare</span>"

        content += "</span>"
        content += "</div>"

        contents[i % 3] += content
        i++;
    })


    html = ""
    for (var i = 0; i < 3; ++i) {
        html += "<div class='post_column'>" + contents[i] + "</div>"
    }
    $("#posts").html(html)
}
