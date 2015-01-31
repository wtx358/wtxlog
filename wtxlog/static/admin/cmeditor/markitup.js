function mycallback(json, ed) {
    var data = $.parseJSON(json);
    var block = ['!', '[', data.msg.localfile, ']', '(', data.msg.url.replace('!', ''), ')'];
    ed.replaceSelection(block.join(''));
    var modal = UIkit.modal("#upload", {center:true});
    modal.hide();
    ed.editor.focus();
}

$(document).ready(function() {
    var htmleditor = UIkit.htmleditor($('.markitup'), {markdown:true, mode:'tab', lineNumbers: true});

    var progressbar = $("#progressbar"),
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
});
