function mycallback(json, ed) {
    var data = $.parseJSON(json);
    var modal = UIkit.modal("#upload");
    if (modal.isActive()) {
        $('#preview').html('<img style="max-height: 300px; max-width: 100%" alt="'+data.msg.localfile+'" src="'+data.msg.url.replace('!', '')+'" />');
    } else {
        var block = ['!', '[', data.msg.localfile, ']', '(', data.msg.url.replace('!', ''), ')'];
        ed.replaceSelection(block.join(''));
    }
}

$(document).ready(function() {
    var htmleditor = UIkit.htmleditor($('.markitup'), {markdown:true, mode:'tab', lineNumbers: true});

    var progressbar = $("#progressbar"),
        preview = $("#preview"),
        bar         = progressbar.find('.uk-progress-bar'),
        settings    = {
            action: '/upload/', // upload url
            param: 'filedata',
            allow : '*.(jpg|jpeg|gif|png)', // allow only images

            loadstart: function() {
                bar.css("width", "0%").text("0%");
                progressbar.removeClass("uk-hidden");
            },

            progress: function(percent) {
                percent = Math.ceil(percent);
                bar.css("width", percent+"%").text(percent+"%");
            },

            allcomplete: function(response) {
                bar.css("width", "100%").text("100%");
                setTimeout(function(){
                    progressbar.addClass("uk-hidden");
                }, 250);
                mycallback(response, htmleditor);
            }
        };
    var select = UIkit.uploadSelect($("#upload-select"), settings),
        drop   = UIkit.uploadDrop($("#upload-drop"), settings),
        drop2  = UIkit.uploadDrop($(".CodeMirror-code"), settings);

    $("#btn_upload_submit").click(function() {
        var preview_img = $('#preview>img');
        var src = preview_img.attr('src'),
        text = preview_img.attr('alt');
        if (typeof(src) == "undefined") {src="http://";}
        var block = ['!', '[', text, ']', '(', src, ')'];
        htmleditor.replaceSelection(block.join(''));
        var modal = UIkit.modal("#upload");
        preview.html('');
        modal.hide();
    })
});
