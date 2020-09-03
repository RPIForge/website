

function toggle_chat(){
	
	document.getElementById("chat_contents").style.display = (document.getElementById("chat_contents").style.display == "block" ? "none" : "block");
	console.log(document.getElementById('chat_iframe').src)
	if(document.getElementById('chat_iframe').src == ''){
		document.getElementById('chat_iframe').src = chat_url;
	}	
}
