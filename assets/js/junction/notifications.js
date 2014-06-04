Molecular.register("notifications_tools", function() {
   $(function() {
        var mark = function(action, id, success, error) {
            jQuery.ajax("/notifications/mark/" + id + "/" + action, {
                success: success,
                error: error
            })
        };

        window.mark_row_viewed = function(element) {
            var row = $(element).closest("li");
            var id = row.data("id");

            mark("read", id, function() {
                row.addClass("read");

                // Decrement the notification count in the header.
                var header_notification_num_display = $('.header-notifcation-num-display');
                header_notification_num_display.html(parseInt(header_notification_num_display.html(), 0) - 1)
            })
        }
   })
});