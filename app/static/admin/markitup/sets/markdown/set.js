// ----------------------------------------------------------------------------
// markItUp!
// ----------------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// ----------------------------------------------------------------------------
myMarkdownSettings = {
    nameSpace: 'markdown',
    // Useful to prevent multi-instances CSS conflict
    previewParserPath: '/preview/',
    onShiftEnter: {
        keepDefault: false,
        openWith: '\n\n'
    },
    markupSet: [{
        name: 'First Level Heading',
        key: "1",
        className: "heading1",
        placeHolder: 'Your title here...',
        closeWith: function(markItUp) {
            return miu.markdownTitle(markItUp, '=')
        }
    },
    {
        name: 'Second Level Heading',
        key: "2",
        className: "heading2",
        placeHolder: 'Your title here...',
        closeWith: function(markItUp) {
            return miu.markdownTitle(markItUp, '-')
        }
    },
    {
        name: 'Heading 3',
        key: "3",
        className: "heading3",
        openWith: '### ',
        placeHolder: 'Your title here...'
    },
    {
        name: 'Heading 4',
        key: "4",
        className: "heading4",
        openWith: '#### ',
        placeHolder: 'Your title here...'
    },
    {
        name: 'Heading 5',
        key: "5",
        className: "heading5",
        openWith: '##### ',
        placeHolder: 'Your title here...'
    },
    {
        name: 'Heading 6',
        key: "6",
        className: "heading6",
        openWith: '###### ',
        placeHolder: 'Your title here...'
    },
    {
        separator: '---------------'
    },
    {
        name: 'Bold',
        key: "B",
        className: "btn_bold",
        openWith: '**',
        closeWith: '**'
    },
    {
        name: 'Italic',
        key: "I",
        className: "btn_italic",
        openWith: '_',
        closeWith: '_'
    },
    {
        separator: '---------------'
    },
    {
        name: 'Bulleted List',
        openWith: '- ',
        className: "btn_ul",
    },
    {
        name: 'Numeric List',
        className: "btn_ol",
        openWith: function(markItUp) {
            return markItUp.line + '. ';
        }
    },
    {
        separator: '---------------'
    },
    {
        name: 'Picture',
        key: "P",
        className: "btn_picture",
        replaceWith: '![[![Alternative text]!]]([![Url:!:http://]!] "[![Title]!]")'
    },
    {
        name: 'UploadPicture',
        key: 'U',
        className: "btn_picture_upload",
        beforeInsert: function(markItUp) {
			if (InlineUpload.dialog) InlineUpload.cleanUp();
			InlineUpload.display(markItUp);
        },
    },
    {
        name: 'Link',
        key: "L",
        className: "btn_link",
        openWith: '[',
        closeWith: ']([![Url:!:http://]!] "[![Title]!]")',
        placeHolder: 'Your text to link here...'
    },
    {
        separator: '---------------'
    },
    {
        name: 'Quotes',
        openWith: '> ',
        className: "btn_quotes",
    },
    {
        name: 'Code Block / Code',
        className: "btn_code",
        openWith: '(!(\t|!|`)!)',
        closeWith: '(!(`)!)'
    },
    {
        name: 'More',
        openWith: '<!--more-->\n',
        className: "btn_more",
    },
	/*
    {
        separator: '---------------'
    },
    {
        name: 'Preview',
        call: 'preview',
        className: "preview"
    },
	*/
    ]
}

// mIu nameSpace to avoid conflict.
miu = {
    markdownTitle: function(markItUp, char) {
        heading = '';
        n = $.trim(markItUp.selection || markItUp.placeHolder).length;
        for (i = 0; i < n; i++) {
            heading += char;
        }
        return '\n' + heading + '\n';
    }
}

var InlineUpload = {
    dialog: null,
    block: '',
    offset: {},
    options: {
        container_class: 'markItUpInlineUpload',
        action: '/upload/',
		holder: 'fileholder',
        close: 'inline_upload_close',
    },
	callback: function(json) {
		data = $.parseJSON(json);
		var block = ['<img src="', data.msg.url.replace('!', ''), '" alt="', data.msg.localfile, '" />'];
		$.markItUp({replaceWith: block.join('')});
		InlineUpload.cleanUp();
	},
	postFile: function(fromfile) {
		xhr = new XMLHttpRequest();
		xhr.onreadystatechange=function(){
			if(xhr.readyState===4) {
				InlineUpload.callback(xhr.responseText);
			}
		};
		xhr.open("POST", InlineUpload.options.action);
		xhr.setRequestHeader('Content-Type', 'application/octet-stream');
		xhr.setRequestHeader('Content-Disposition', 'attachment; name="filedata"; filename="'+encodeURIComponent(fromfile.name)+'"');
		if (xhr.sendAsBinary&&fromfile.getAsBinary) {
			xhr.sendAsBinary(fromfile.getAsBinary());
		}
		else {
			xhr.send(fromfile);
		}
	},
    display: function(hash) {
        var self = this;
        /* Find position of toolbar. The dialog will inserted into the DOM elsewhere
         * but has position: absolute. This is to avoid nesting the upload form inside
         * the original. The dialog's offset from the toolbar position is adjusted in
         * the stylesheet with the margin rule.
         */
        this.offset = $(hash.textarea).prev('.markItUpHeader').offset();
        /* We want to build this fresh each time to avoid ID conflicts in case of
         * multiple editors. This also means the form elements don't need to be
         * cleared out.
         */

        this.dialog = $(['<div class="', this.options.container_class, '"><div id="', this.options.holder, '"><img id="loading" src="/static/admin/markitup/loading.gif" style="width:16px;height:16px; display:none;">拖放文件到这里 或者 <a id="selectfile" href="#" >选择文件上传</a><input type="file" name="filedata" id="filedata" style="opacity: 0; cursor: pointer; position: absolute; width: 78px; height: 15px; left: 112.5px; top: 36.75px;" /></div><div id="inline_upload_close"></div></div>'].join('')).appendTo(document.body).hide().css('top', this.offset.top).css('left', this.offset.left);
        
		$('#selectfile').click(function() {
			$('#filedata').click();
        });
		
		$('#filedata').change(function () {
			if (window.FormData) {
				var formData = new FormData();
				formData.append('filedata', document.getElementById('filedata').files[0]);
				var xhr = new XMLHttpRequest();
				xhr.open('POST', InlineUpload.options.action);
				xhr.onload = function () {
					if (xhr.status === 200) {
						InlineUpload.callback(xhr.responseText);
					} else {
						alert("error");
					}
				};
				xhr.send(formData);
				$("#loading").show();
			} else {
			alert('this browser can\'t not be supported, please use Firefox, Opera, Chrome...');
			}
		});
        /* init cancel button */
        $('#' + this.options.close).click(this.cleanUp);
        
		/* Finally, display the dialog */
        this.dialog.fadeIn('slow');
		
		/* drag upload */
		if('draggable' in document.createElement('span')){
			var holder = document.getElementById('fileholder');
			holder.ondragover = function () { this.className = 'hover'; return false; };
			holder.ondragend = function () { this.className = ''; return false; };
			holder.ondrop = function (event) {
				event.preventDefault();
				this.className = '';
				var files = event.dataTransfer.files;
				$("#loading").show();
				InlineUpload.postFile(files[0]);
			};
		}
    },
    cleanUp: function() {
        InlineUpload.dialog.fadeOut().remove();
    }
};
