$(function(){
	$("#time").text(currentTime()).css("margin-right", "1px");
	//$("td").css("width", "10%");
	//$("table").css("width", "67%").css("margin", "0px auto").css("font-size", "12px");
	$("form").css("width", "50%").css("margin", "0px auto").css("font-size", "12px");
	//$("footer").css("background", "linear-gradient(#0bc, #fff)");
	//$("nav").css("background", "linear-gradient(#6cc, #ccc)");
	$(".roleselector").click(function(){
		var count = 0;
		//首先显示所有的记录
		$(".table").find("tr[id!='tbhead']").each(function(){
			$(this).children("#rank").text($(this).children("#rank").attr("record"));
			$(this).show();
		});
		//根据_value属性值，将对应的记录隐藏
		var _value = $(this).attr("_value");
		if(_value == 'ALL')
			return true;
		$(".table").find("td[id='role']").each(function(){
			if($(this).text().indexOf(_value)==-1){
				$(this).parent("tr").hide();
				count++;
			}
			else{
				$(this).siblings("#rank").attr('record', $(this).siblings("#rank").text());
				$(this).siblings("#rank").text($(this).siblings("#rank").text() - count);
			}
		});
	});
	$("#randomCodeImg").click(function(){
		var $img_src = $(this).attr("src");
		$img_src = $img_src + "0";
		$(this).attr("src", $img_src);
	});
	$("#submit").click(function(){
		if($.trim($("#suggestion").val()) == ""){
			alert("请确认已经输入您的建议！");
			return false;
		}
	});
})

function currentTime(){
	var d = new Date();
	time = "";
	time += d.getFullYear() + "-";
	time += d.getMonth() + 1 + "-";
	time += d.getDate();
	return time
}