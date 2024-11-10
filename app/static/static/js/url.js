function toggleMenu(menuIcon) {
    const options = menuIcon.nextElementSibling;
    options.style.display = options.style.display === "none" || options.style.display === "" ? "block" : "none";
    document.addEventListener("click", function handleClickOutside(event) {
        if (!menuIcon.contains(event.target) && !options.contains(event.target)) {
            options.style.display = "none";
            document.removeEventListener("click", handleClickOutside);
        }
    });
}

function toggleDiv(button) {
    const commentId = button.closest('.comment').dataset.commentId;
    const replyBox = document.getElementById(`comment-reply-box-${commentId}`);
    
    if (replyBox.style.display === "none" || replyBox.style.display === "") {
        replyBox.style.display = "block";
    } else {
        replyBox.style.display = "none";
    }
}
