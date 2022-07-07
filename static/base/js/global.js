function ajaxSubmitForm(formName, formCheck, callback) {
    // AJAX代替form标签提交表单

    // 检查元素是否是表单
    const form = document.querySelector('form[name="' + formName + '"]');
    if (form === null || form.nodeName !== 'FORM') {
        return undefined;
    }

    // 监听表单提交事件
    const submitBtn = form.querySelector('button[type="submit"]');
    form.allowSubmit = true;
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        // 防止提交太快
        if (!form.allowSubmit) {
            return undefined;
        }
        submitBtn.setAttribute('disabled', '');
        form.allowSubmit = false;

        // 表单验证
        if (formCheck !== undefined && !formCheck(form)) {
            submitBtn.removeAttribute('disabled');
            form.allowSubmit = true;
            return undefined;
        }

        // 发送表单
        ajax.post(form.action, new FormData(form), function (data) {
            callback(data);
            submitBtn.removeAttribute('disabled');
            form.allowSubmit = true;
        });
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