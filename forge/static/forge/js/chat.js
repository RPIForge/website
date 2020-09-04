

function toggle_chat(){
	var chat_container =  document.getElementById("chat_container");
	var chat_contents = document.getElementById("chat_contents");
	var chat_footer = document.getElementById("chat_footer_tab");
	var chat_iframe = document.getElementById('chat_iframe')
	
	
	
	if(chat_contents.style.display=="block"){
		chat_container.style.width = "5vw";
		chat_contents.style.display = "none";
		chat_footer.style.height = "";
		
	} else {
		chat_contents.style.display = "block";
		chat_container.style.width = "20vw";
		chat_footer.style.height = "3%";
	}
	
	if(chat_iframe.src == ''){
		chat_iframe.src = chat_url;
	}	
}	

function resize_chat(obj){
	
	
}
