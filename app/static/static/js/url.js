let header = document.querySelector("header");
let main = document.querySelector("main");
main.style.paddingTop = header.offsetHeight + "px";
let link = document.querySelector(".links");

function menu() {
    link.classList.toggle("active");
}

function toggleMenu(menuIcon) {
    const options = menuIcon.nextElementSibling; // Select the comment-options div
    options.style.display = options.style.display === "none" || options.style.display === "" ? "block" : "none";
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
