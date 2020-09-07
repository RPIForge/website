var logout_event;

function notify() {
	alert("Logged out automatically due to inactivity.");
}

 
function automatic_logout() {
	location.replace("/logout");
	setTimeout(notify, 10);
}


logout_event = setTimeout(automatic_logout, 1000 * 60 * 10);

document.onclick = function() {
	clearTimeout(logout_event);
	logout_event = setTimeout(automatic_logout, 1000 * 60 * 10);
}