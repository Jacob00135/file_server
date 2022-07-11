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
        xhr.open('get', url, true);
        xhr.send();
        xhr.addEventListener('readystatechange', function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                callback(JSON.parse(xhr.responseText));
            }
        });
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
    },
    'getFile': function (url, callback) {
        const xhr = new XMLHttpRequest();
        xhr.open('get', url, true);
        xhr.send();
        xhr.responseType = 'blob';
        xhr.addEventListener('readystatechange', function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                const file = xhr.response;
                const splitList = xhr.getResponseHeader('content-disposition').split("'");
                file.name = decodeURI(splitList[splitList.length - 1]);
                callback(file);
            }
        });
    }
}

function showWarningModal(message, title) {
    const modal = document.querySelector('#warning-modal');
    modal.querySelector('.modal-body > p').innerText = message;
    if (title !== undefined) {
        modal.querySelector('.modal-title').innerText = title;
    }
    $('#warning-modal').modal('show');
}

function downloadDir(url, zipName) {
    // 获取该目录下所有的文件名
    ajax.get(url, function (data) {
        // 检查请求是否成功
        if (data.status === 0) {
            showWarningModal('下载失败');
            return undefined;
        }

        // 检查是否为空目录
        const fileNameList = data['file_name_list'];
        if (fileNameList.length === 0) {
            showWarningModal('该目录是空目录！');
            return undefined;
        }

        // 构建文件下载网址
        const fileUrlList = [];
        for (let i = 0; i < fileNameList.length; i++) {
            fileUrlList.push(url + '&filename=' + fileNameList[i]);
        }

        // 下载文件
        showWarningModal('正在下载...请不要离开此页面');
        recursionDownloadFile(fileUrlList, zipName, new JSZip());
    });
}

function recursionDownloadFile(fileUrlList, zipName, jsZipObject) {
    ajax.getFile(fileUrlList.shift(), function (file) {
        jsZipObject.file(file.name, file);
        if (fileUrlList.length === 0) {
            jsZipObject.generateAsync({'type': 'blob'}).then(function (content) {
                saveAs(content, zipName + '.zip');
                showWarningModal('下载完毕');
            });
        } else {
            showWarningModal('下载成功：' + file.name);
            recursionDownloadFile(fileUrlList, zipName, jsZipObject);
        }
    });
}
