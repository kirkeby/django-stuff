(function () {
    var req = false;
    try {
        req = new ActiveXObject("Msxml2.XMLHTTP");
    } catch (e) {
        try {
            req = new ActiveXObject("Microsoft.XMLHTTP");
        } catch (f) {
            req = false;
        }
    }
    if(! req && typeof XMLHttpRequest != 'undefined') {
        req = new XMLHttpRequest();
    }

    if(req) {
        var path = '/scryer/?url=' + escape(document.location);
        path = path + '&ref=' + escape(document.referrer);
        path = path + '&qux=' + (new Date()).getTime();
        req.open("GET", path, true);
        req.send("");
    }
}
)();
