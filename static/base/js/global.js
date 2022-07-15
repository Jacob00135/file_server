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

function ajaxUploadFile(formName, formCheck, uploadCallback, responseCallback) {
    // AJAX代替form标签上传文件

    // 检查元素是否是表单
    const form = document.querySelector('form[name="' + formName + '"]');
    if (form === null || form.nodeName !== 'FORM') return undefined;

    // 监听表单提交事件
    const submitBtn = form.querySelector('button[type="submit"]');
    form.allowSubmit = true;
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        // 防止提交太快
        if (!form.allowSubmit) return undefined;
        submitBtn.setAttribute('disabled', '');
        form.allowSubmit = false;

        // 表单验证
        if (formCheck !== undefined && !formCheck(form)) {
            submitBtn.removeAttribute('disabled');
            form.allowSubmit = true;
            return undefined;
        }

        // 上传文件
        ajax.uploadFile(form.action, new FormData(form), uploadCallback, function (data) {
            responseCallback(data);
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
                callback(xhr.response);
            }
        });
    },
    'uploadFile': function (url, formData, uploadCallback, responseCallback) {
        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', function (e) {
            if (e.lengthComputable) {
                const value = Math.ceil((e.loaded / e.total) * 100);
                uploadCallback(value);
            }
        });

        xhr.open('post', url, true);
        xhr.send(formData);
        xhr.addEventListener('readystatechange', function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                responseCallback(JSON.parse(xhr.responseText));
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
        const fileInfo = {
            'name': fileNameList,
            'url': []
        };
        for (let i = 0; i < fileNameList.length; i++) {
            fileInfo['url'].push(url + '&filename=' + fileNameList[i]);
        }

        // 下载文件
        showWarningModal('正在下载...请不要离开此页面');
        recursionDownloadFile(fileInfo, zipName, new JSZip());
    });
}

function recursionDownloadFile(fileInfo, zipName, jsZipObject) {
    ajax.getFile(fileInfo['url'].shift(), function (file) {
        jsZipObject.file(fileInfo['name'].shift(), file);
        if (fileInfo['url'].length === 0) {
            jsZipObject.generateAsync({'type': 'blob'}).then(function (content) {
                saveAs(content, zipName + '.zip');
                showWarningModal('下载完毕');
            });
        } else {
            recursionDownloadFile(fileInfo, zipName, jsZipObject);
        }
    });
}

function addSearchParam(url, param) {
    if (url.indexOf('?') < 0) {
        url = url + '?';
    } else {
        url = url + '&';
    }
    let ls = [];
    Object.keys(param).forEach((k) => {
        ls.push([k, '=', param[k]].join(''));
    });
    return url + ls.join('&');
}

