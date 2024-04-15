var footerResizeEvent = new Event('footerResize');

function autoExpand(textArea) {
    textArea.style.height = 'auto';

    var rows = textArea.value.split('\n').length;
    rows = Math.min(rows, 7);

    textArea.rows = rows;

    document.querySelector('.content-foot').dispatchEvent(footerResizeEvent);
}

function setMaxHeight() {
    var headerHeight = document.querySelector('.content-header').offsetHeight;
    var footerHeight = document.querySelector('.content-foot').offsetHeight;
    var contentBody = document.querySelector('.content-body');
    var maxHeight = window.innerHeight - (headerHeight + footerHeight);
    contentBody.style.maxHeight = maxHeight + 'px';
}

window.addEventListener('resize', setMaxHeight);
document.querySelector('.content-foot').addEventListener('footerResize', setMaxHeight);
setMaxHeight();

function updateDbId(id) {
    // Send AJAX request to Flask backend
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/update_db_id", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            console.log("DB ID updated successfully");
            window.location.reload();
        }
    };
    xhr.send(JSON.stringify({ id: id }));
}