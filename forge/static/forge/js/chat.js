
function getWidth() {
  return Math.max(
    document.body.scrollWidth,
    document.documentElement.scrollWidth,
    document.body.offsetWidth,
    document.documentElement.offsetWidth,
    document.documentElement.clientWidth
  );
}

function getHeight() {
  return Math.max(
    document.body.scrollHeight,
    document.documentElement.scrollHeight,
    document.body.offsetHeight,
    document.documentElement.offsetHeight,
    document.documentElement.clientHeight
  );
}


function toggle_chat(){
	var chat_container =  document.getElementById("chat_container");
	var chat_contents = document.getElementById("chat_contents");
	var chat_footer = document.getElementById("chat_footer_tab");
	var chat_iframe = document.getElementById('chat_iframe')
	
	
	
	if(chat_contents.style.display=="block"){
		var new_width = Math.min(getWidth()*0.50,256);
		console.log(screen.width);
		chat_container.style.minWidth  =  new_width+"px";
		chat_contents.style.display = "none";
		chat_footer.style.height = "";
		
	} else {
		chat_contents.style.display = "block";
		var new_width = Math.min(getWidth()*0.94,512);
		console.log(screen.width);
		chat_container.style.minWidth  =  new_width+"px";
		chat_footer.style.height = "3%";
	}
	
	if(chat_iframe.src == ''){
		chat_iframe.src = chat_url;
	}	
}	

function resize_chat(obj){
	
	
}
