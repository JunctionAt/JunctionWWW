$(document).ready(function() {
    list = $(".subreddit-recent");

    $.ajax({
      url: "https://pay.reddit.com/r/junction/new.json?limit=4",
      type: "get",
      dataType: "jsonp",
      jsonp: "jsonp",
      success: function(data) {
        var posts = data.data.children;
          $(".subreddit-recent .loading").remove();
            for(var i=0; i < posts.length; i++) {
              var post = posts[i];
              list.append("<li><a href=\"" + post.data.url + "\">"+ post.data.title +"</a></li>");
            }
      }
    });
});
