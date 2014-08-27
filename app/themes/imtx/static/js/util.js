//侧栏跟随
(function(){
	var oDiv=document.getElementById("float");
	if (oDiv==null) return false;
	var H=0,iE6;
	var Y=oDiv;
	if ($(window).width() <= 650) { return; }
	while(Y){H+=Y.offsetTop;Y=Y.offsetParent};
	iE6=window.ActiveXObject&&!window.XMLHttpRequest;
	if(!iE6){
		window.onscroll=function()
		{
			var s=document.body.scrollTop||document.documentElement.scrollTop;
			if(s>H){oDiv.className="div1 div2";if(iE6){oDiv.style.top=(s-H)+"px";}}
			else{oDiv.className="div1";}	
		};
	}

})();

/* back top */
$(window).scroll(function () {
    var dt = $(document).scrollTop();
    var wt = $(window).height();
    if (dt <= 0) {
      $("#top_btn").hide();
      return;
    }
    $("#top_btn").show();
    if ($.browser.msie && $.browser.version == 6.0) {//IE6返回顶部
      $("#top_btn").css("top", wt + dt - 110 + "px");
    }
  });
  $("#top_btn").click(function () { $("html,body").animate({ scrollTop: 0 }, 200) });

function gethits(id, out)
{
  //$('#'+out).html("<img src=\"/_themes/imtx/images/loading.gif\" />");
  $.ajax({
    type: "get",
    cache:false,
    url: '/api/gethits/?id='+id,
    timeout: 20000,
    error: function(){$('#'+out).html('failed');},
    success: function(t){$('#'+out).html(t);}
  });
}
