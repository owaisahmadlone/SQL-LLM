function autoExpand(textArea) {
    textArea.style.height = 'auto';

    var rows = textArea.value.split('\n').length;
    rows = Math.min(rows, 7);

    textArea.rows = rows;
    
    var footerResizeEvent = new Event('footerResize');
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