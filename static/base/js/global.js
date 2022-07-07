function ajaxSubmitForm(formSelector, callback) {
    // AJAX代替form标签提交表单
    const form = document.querySelector(formSelector);
    if (form === null || form.nodeName !== 'FORM') {
        return undefined;
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        ajax.post(form.action, new FormData(form), callback);
    });
}

window.ajax = {
    'get': function (url, callback) {
        const xhr = new XMLHttpRequest();
        xhr.addEventListener('readystatechange', function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                callback(JSON.parse(xhr.responseText));
            }
        });
        xhr.open('get', url, true);
        xhr.send();
    },
    'post': function (url, formData, callback) {
        const xhr = new XMLHttpRequest();
        xhr.addEventListener('readystatechange', function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                callback(JSON.parse(xhr.responseText));
            }
        });
        xhr.open('post', url, true);
        xhr.send(formData);
    }
}

function showWarningModal(message) {
    $('#warning-modal').modal('show');
    document.querySelector('#warning-modal .modal-body > p').innerText = message;
}