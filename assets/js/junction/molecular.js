/**
 * Created by HansiHE on 11/30/13.
 */

(function() {

    Molecular = {};

    Molecular.register = function(name, func) {
        if(to_load.indexOf(name) > -1) {
            func();
        }
    };

    var to_load;
    if(document.head.getAttribute("data-molecules")) {
        to_load = document.head.getAttribute("data-molecules").split(" ");
    } else {
        to_load = [];
    }

})();
