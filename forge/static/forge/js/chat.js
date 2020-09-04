

function toggle_chat(){
	
	if(document.getElementById("chat_contents").style.display=="block"){
		document.getElementById("chat_contents").style.display = "none";
		document.getElementById("chat_footer_tab").style.height = "";
	} else {
		document.getElementById("chat_contents").style.display = "block";
		document.getElementById("chat_footer_tab").style.height = "3%";
	}
	console.log(document.getElementById('chat_iframe').src)
	if(document.getElementById('chat_iframe').src == ''){
		document.getElementById('chat_iframe').src = chat_url;
	}	
	
}
