jQuery(document).ready(function($) {
	$('a.edit-link').click(function(event){
        var root = $(this).closest('div.post-root');
        root.find('div.forum-post-rendered').hide();
        root.find('div.forum-post-edit').show();
        root.find('div.forum-post-edit textarea').val(
            root.find('div.forum-post-raw').text()
        );
	    return false;
	});
    $('a.quote-link').click(function(event){
        var root = $(this).closest('div.post-root');
        var post = root.find('div.forum-post-raw').text();
        var textarea = $('#post-reply').find('textarea');
        textarea.val(textarea.val() + '> ' + post.split("\n").join("\n> "));
        location.href = '#post-reply';
	    return false;
	});
});