function load_json(url, callback)
{
    var req = data = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if(req.readyState == 4) {
            // only if "OK"
            if(req.status == 200) {
                try {
                    var value = eval('(' + req.responseText + ')');
                } catch(e) {
                    alert("Error in JSON: " + req.responseText);
                }
                try {
                    callback(value);
                } catch(e) {
                    alert("Error in callback: " + e.message);
                }
            } else {
                alert("There was a problem retrieving the XML data:\n" +
                      req.statusText);
            }
        }
    };
    req.open('GET', 'unread-posts/?format=json', true);
    req.send('');
}

function load_xml(url, callback)
{
    var req = data = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if(req.readyState == 4) {
            // only if "OK"
            if(req.status == 200) {
                try {
                    callback(req.responseXML);
                } catch(e) {
                    alert("Error in callback: " + e.message);
                }
            } else {
                alert("There was a problem retrieving the XML data:\n" +
                      req.statusText);
            }
        }
    };
    req.open('GET', 'unread-posts/?format=json', true);
    req.send('');
}

load_xml('unread-posts/?format=xml', function(values) {
    var xml = values.posts[0].xhtml;
    var parser = new DOMImplementation();
    //var doc = parser.loadXML(xml);
    //var root = doc.getDocumentElement();
    //alert(root);
    alert(parser);
});
