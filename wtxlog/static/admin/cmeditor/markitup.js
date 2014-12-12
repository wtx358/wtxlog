var editor_obj = $('.markitup')[0];

function mycallback(json, ed) {
	var data = $.parseJSON(json);
	var block = ['!', '[', data.msg.localfile, ']', '(', data.msg.url.replace('!', ''), ')'];
	ed.replaceSelection(block.join(''));
	ed.focus();
}

function upload(fromfile, editor) {
	xhr = new XMLHttpRequest();
	xhr.onreadystatechange=function(){
		if(xhr.readyState===4) {
			mycallback(xhr.responseText, editor);
		}
	};
	xhr.open("POST", "/upload/");
	xhr.setRequestHeader('Content-Type', 'application/octet-stream');
	xhr.setRequestHeader('Content-Disposition', 'attachment; name="filedata"; filename="'+encodeURIComponent(fromfile.name)+'"');
	if (xhr.sendAsBinary&&fromfile.getAsBinary) {
		xhr.sendAsBinary(fromfile.getAsBinary());
	}
	else {
		xhr.send(fromfile);
	}
}

CodeMirror.commands.save = function(){ /*alert("Saving");*/ $("input[name$='_continue_editing']").click();  };
//var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
var editor = CodeMirror.fromTextArea(editor_obj, {
	lineNumbers: true,
	lineWrapping: true,
	styleActiveLine: true,
	mode: "markdown",
	keyMap: "vim",
	matchBrackets: true,
	showCursorWhenSelecting: true,
	showTrailingSpace: true,
	dragDrop: true,
	extraKeys: {
		"Enter": "newlineAndIndentContinueMarkdownList",
		"F11": function(cm) {
		  cm.setOption("fullScreen", !cm.getOption("fullScreen"));
		},
	},
});

CodeMirror.on(editor, "drop", function (editor, e) {
	e.preventDefault(); 
	var files = e.dataTransfer.files; upload(files[0], editor); 
});

/*
var commandDisplay = document.getElementById('command-display');
var keys = '';
CodeMirror.on(editor, 'vim-keypress', function(key) {
	keys = keys + key;
	commandDisplay.innerHTML = keys;
});
CodeMirror.on(editor, 'vim-command-done', function(e) {
	keys = '';
	commandDisplay.innerHTML = keys;
});
*/