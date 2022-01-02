$(document).ready(function(){

    function ChangeRes(w, h){
        var data = new FormData();
        data.append('width', w);
        data.append('height', h);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/setparams', true);
        xhr.send(data);
    }

    $("#low").click(function(){
        ChangeRes(320, 240);
	})

	$("#norm").click(function(){
        ChangeRes(640, 480);
	})

	$("#hi").click(function(){
        ChangeRes(800, 600);
	})

	// $(':checkbox').checkboxpicker().change(function() {
 //        if($('input[name="agree"]:checked').length > 0) {
 //            document.getElementById("videofield").src="video_feed?fd=true";
 //        }
 //        else{
 //            document.getElementById("videofield").src="video_feed?fd=false";
 //        }
 //    });

    $("button").click(function(){
        var data = new FormData();
        var cmd = $(this).attr("cmd");
        data.append('cmd', cmd);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/command', true);
        // xhr.onload = function(oEvent) {
        //     if (xhr.status == 200) {
        //       console.log("done!");
        //     } else {
        //       console.log("Error " + xhr.status);
        //     }
        // };
        xhr.send(data);
    })
});