var logout_event;

function notify() {
	alert("Logged out automatically due to inactivity.");
}

 
function automatic_logout() {
    
    if(typeof disable_logout !== 'undefined' && disable_logout){
        logout_event = setTimeout(automatic_logout, 1000 * 60 * 10);
        return;
    }
    
    location.replace("/logout");
	setTimeout(notify, 10);
}

logout_event = setTimeout(automatic_logout, 1000 * 60 * 10);

function update_logout() {
	clearTimeout(logout_event);
	logout_event = setTimeout(automatic_logout, 1000 * 60 * 10);
}

