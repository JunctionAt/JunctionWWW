/**
 * Created by HansiHE on 11/30/13.
 */

/*

This is to make inline content editing easy. I wrote this because we are doing that a lot.

To make a target editable, you need two things.
1. A template. This defines what happens when you set a thing to be editable.
    A template needs to have a data-editable attribute with a template id, and the class content-editable-template.
    When a target is set to be editable, the element with a edit tag within the template is copied over to the target.
2. A target. Multiple of these can exist for each template.
    It needs a data-editable attribute with a template id, content-editable class, and a unique id.
    To set a target to be editable, call Editable.set_editable(id).

 */

Molecular.register("editable", function() {
    $(function() {
        // Get all the editable templates, put them into a dict by identifier
        var editable_srcs = $(".content-editable-template");
        var editable_templates = {};
        editable_srcs.each(function(index, element) {
            editable_templates[$(element).data("editable")] = element;
        });

        Editable = {};
        Editable.handlers = {};
        Editable.set_editable = function(element) {
            var target = $(element);
            if(target.length == 0) {
                return false;
            }

            if(!target.hasClass("content-editable")) {
                target = target.parents(".content-editable");
            }

            if(target.hasClass("editing")) {
                return false;
            }
            target.addClass("editing");

            var identifier = target.data("editable");

            var template = $(editable_templates[identifier]);
            $(template.children(".edit")[0]).clone().appendTo(target);

            if(identifier in Editable.handlers && "enable" in Editable.handlers[identifier]) {
               Editable.handlers[identifier].enable(target);
            }

            return true;
        };

        Editable.set_viewable = function(element) {
            var target = $(element);
            if(target.length == 0) {
                return false;
            }

            if(!target.hasClass("content-editable")) {
                target = target.parents(".content-editable");
            }

            if(!target.hasClass("editing")) {
                return false;
            }
            target.removeClass("editing");

            var identifier = target.data("editable");
            if(identifier in Editable.handlers && "disable" in Editable.handlers[identifier]) {
               Editable.handlers[identifier].disable(target);
            }

            target.children(".edit").remove();

            return true;
        };

    })
});