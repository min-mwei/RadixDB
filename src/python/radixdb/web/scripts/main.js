function showImage(blob) {
    var  output = document.getElementById("output");
    var img = new Image();
    img.src = blob
    output.appendChild(img);
}

function showText(data) {
    console.log("clicked:", data);
    var output = document.getElementById("output");
    let text = document.createElement('div');
    text.innerHTML = data;
    output.appendChild(text);
    output.appendChild(document.createElement("br"));
}

function clearOutput() {
    console.log("clicked:", "clear");
    var output = document.getElementById("output");
    while (output.firstChild) {
        output.firstChild.remove();
    }
}

function run() {
    //var editor = document.getElementById('editor');
    code = editor.getValue();
    console.log("code:", code)
    const url = "/query";
    console.log("sending:", JSON.stringify({'query': code}));
    query_result = fetch(url, {
        method : "POST",
        body: code
    }).then(response => {
	ct = response.headers.get('Content-Type');
	(async() => {
	    if (ct == 'application/json') {
		result = await response.json();
		if ('text' in result)
		    showText(result['text']);
		if ('plot' in result)
		    showImage(result['plot']);
	    }
	})();});
}
