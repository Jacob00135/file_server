(function (window, document) {
    const fileList = document.querySelector('#file-list');
    const typeList = document.querySelectorAll('#file-list > li.list-group-item > .type');
    const fullNameBtnList = document.querySelectorAll('#file-list .show-full-name');
    const downloadBtnList = document.querySelectorAll('#file-list .download-dir');
    const modalDownloadBtn = document.querySelector('#download-modal .download');
    const renameForm = document.querySelector('form[name="rename"]');
    const renameBtnList = document.querySelectorAll('#file-list .rename');
    const renameWarning = document.querySelector('#rename-warning');
    const copyForm = document.querySelector('form[name="copy"]');
    const copyBtnList = document.querySelectorAll('#file-list .copy');
    const copyWarning = document.querySelector('#copy-warning');
    const copyInfo = document.querySelector('#copy-info');
    const moveForm = document.querySelector('form[name="move"]');
    const moveBtnList = document.querySelectorAll('#file-list .move');
    const moveWarning = document.querySelector('#move-warning');
    const moveInfo = document.querySelector('#move-info');
    const removeBtnList = document.querySelectorAll('#file-list .remove');
    const decideRemoveBtn = document.querySelector('#remove-modal .remove');
    const removeWarning = document.querySelector('#remove-warning');
    const removeInfo = document.querySelector('#remove-info');
    const uploadFileForm = document.querySelector('form[name="upload-file"]');
    const uploadFileInput = document.querySelector('form[name="upload-file"] input[type="file"]');
    const uploadWarning = document.querySelector('#upload-warning');
    const uploadInfo = document.querySelector('#upload-info');
    const uploadFileProgress = document.querySelector('#upload-file-progress');
    const pageNav = document.querySelector('#page-nav');
    const iconfontMap = {
        'dir': 'glyphicon-folder-open',
        'text': 'glyphicon-file',
        'image': 'glyphicon-picture',
        'audio': 'glyphicon-music',
        'video': 'glyphicon-film',
        'package': 'glyphicon-compressed',
        'other': 'glyphicon-question-sign'
    };

    // 加载分页导航
    if (pageNav !== null) {
        // 获取导航信息
        const page = parseInt(pageNav.getAttribute('data-page'));
        const pageCount = parseInt(pageNav.getAttribute('data-page-count'));
        const baseUrl = pageNav.getAttribute('data-base-url');
        const ul = pageNav.querySelector('ul.pagination');
        const first = ul.querySelector('li.first');
        const last = ul.querySelector('li.last');

        // 获取一个分页导航中的链接
        function getLi(page) {
            const li = document.createElement('li');
            const a = document.createElement('a');

            a.href = addSearchParam(baseUrl, {'page': page});
            a.innerHTML = page;
            li.appendChild(a);
            return li;
        }

        // 获取一个分页导航中的省略号
        function getEl() {
            const li = document.createElement('li');
            const a = document.createElement('a');

            li.classList.add('disabled');
            li.classList.add('ellipsis');
            a.href = 'javascript:;';
            a.innerHTML = '...';
            li.appendChild(a);
            return li;
        }

        // 处理数字页码
        first.querySelector('a').href = addSearchParam(baseUrl, {'page': 1});
        last.querySelector('a').href = addSearchParam(baseUrl, {'page': pageCount});
        if (pageCount <= 5) {
            for (let i = 2; i < pageCount; i++) {
                ul.insertBefore(getLi(i), last);
            }
        } else {
            const numberList = [];
            if (page === pageCount) numberList.push(pageCount - 2);
            if (page - 1 > 1) numberList.push(page - 1);
            if (page !== 1 && page !== pageCount) numberList.push(page);
            if (page + 1 < pageCount) numberList.push(page + 1);
            if (page === 1)  numberList.push(3);
            numberList.forEach((value) => {
                ul.insertBefore(getLi(value), last);
            })

            // 插入省略号页码
            const li3 = ul.children[2];
            const liLowest3 = ul.children[ul.children.length - 3];
            if (parseInt(li3.querySelector('a').innerHTML) - 1 >= 2) ul.insertBefore(getEl(), li3);
            if (pageCount - parseInt(liLowest3.querySelector('a').innerHTML) >= 2) ul.insertBefore(getEl(), last);
        }

        // 使当前页的页码处于激活状态
        for (let i = 0; i < ul.children.length; i++) {
            let children = ul.children[i];
            if (children.querySelector('a').innerHTML === String(page)) {
                children.classList.add('active');
                children.querySelector('a').href = 'javascript:;';
                break;
            }
        }

        // 处理上一页、下一页页码
        const prev = ul.children[0];
        const next = ul.children[ul.children.length - 1];
        if (page === 1) {
            prev.classList.add('disabled');
            next.querySelector('a').href = addSearchParam(baseUrl, {'page': page + 1});
        } else if (page === pageCount) {
            prev.querySelector('a').href = addSearchParam(baseUrl, {'page': page - 1});
            next.classList.add('disabled');
        } else {
            prev.querySelector('a').href = addSearchParam(baseUrl, {'page': page - 1});
            next.querySelector('a').href = addSearchParam(baseUrl, {'page': page + 1});
        }

        // 跳转页面的输入页码监听事件
        document.getElementById('jump-page').addEventListener('input', function (e) {
            this.value = this.value.replace(/\D/g, '');
            const newValue = parseInt(this.value);
            if (isNaN(newValue) || newValue <= 0) {
                this.value = 1;
            } else if (newValue > pageCount) {
                this.value = pageCount;
            }
        });

        // 跳转按钮点击事件
        pageNav.querySelector('.jump-page-btn').addEventListener('click', function (e) {
            const jumpPage = document.getElementById('jump-page').value || 1;
            location.href = addSearchParam(baseUrl, {'page': jumpPage});
        });
    }

    // 渲染文件类型对应的字体图标
    for (let i = 0; i < typeList.length; i++) {
        let t = typeList[i];
        let type = t.getAttribute('data-type');
        t.classList.add(iconfontMap[type]);
    }

    // 查看完整文件名功能
    for (let i = 0; i < fullNameBtnList.length; i++) {
        fullNameBtnList[i].addEventListener('click', function (e) {
            showWarningModal(fileList.children[i].querySelector('.name a').innerHTML, '完整文件名');
        })
    }

    // 打包下载目录功能
    for (let i = 0; i < downloadBtnList.length; i++) {
        downloadBtnList[i].addEventListener('click', function (e) {
            const a = fileList.children[i].querySelector('.name a');
            modalDownloadBtn.setAttribute('data-url', this.getAttribute('data-href'));
            modalDownloadBtn.setAttribute('data-dir-name', a.innerHTML);
            $('#download-modal').modal('show');
        });
    }

    // 下载模态框的“继续下载”按钮的点击事件
    modalDownloadBtn.addEventListener('click', function (e) {
        const url = this.getAttribute('data-url');
        const dirName = this.getAttribute('data-dir-name');
        downloadDir(url, dirName);
    });

    // “重命名”按钮的点击事件
    for (let i = 0; i < renameBtnList.length; i++) {
        renameBtnList[i].addEventListener('click', function (e) {
            let oldName = fileList.children[i].querySelector('.name a').innerHTML;
            if (oldName.indexOf('\\') >= 0) {
                const splitList = oldName.split('\\');
                oldName = splitList[splitList.length - 1];
            }
            renameForm.action = this.getAttribute('data-href');
            renameForm.querySelector('#old-name').value = oldName;
            renameForm.querySelector('input[name="new-name"]').value = '';
            $('#rename-modal').modal('show');
        });
    }

    // 重命名表单的提交事件
    ajaxSubmitForm(
        'rename',
        function (form) {
            // 检查新文件名是否包含\/:*?"<>|
            const oldName = form.querySelector('#old-name').value.toLowerCase();
            const newName = form.querySelector('input[name="new-name"]').value.toLowerCase();
            if (newName.indexOf('\\/:*?"<>|') >= 0) {
                renameWarning.innerHTML = '文件名不能有\\/:*?"<>|字符！';
                renameWarning.classList.remove('hidden');
                return false;
            }

            // 检查新旧文件名是否相同
            if (oldName.toLowerCase() === newName.toLowerCase()) {
                renameWarning.innerHTML = '新旧文件名不能相同！';
                renameWarning.classList.remove('hidden');
                return false;
            }

            return true;
        },
        function (data) {
            if (data.status === 0) {
                renameWarning.innerHTML = data.message;
                renameWarning.classList.remove('hidden');
            } else {
                location.reload();
            }
        }
    );

    // “复制”按钮的点击事件
    for (let i = 0; i < copyBtnList.length; i++) {
        copyBtnList[i].addEventListener('click', function (e) {
            copyForm.action = this.getAttribute('data-href');
            copyForm.querySelector('#source-path').value = this.getAttribute('data-source-path');
            copyForm.querySelector('#target-path').value = '';
            $('#copy-modal').modal('show');
        });
    }

    // 复制表单的提交事件
    ajaxSubmitForm(
        'copy',
        function (form) {
            // 检查目标路径是否包含'\\'
            const sourcePath = form.querySelector('#source-path').value.toLowerCase();
            const targetPath = form.querySelector('#target-path').value.toLowerCase();
            if (targetPath.indexOf('\\') < 0) {
                copyWarning.innerHTML = '路径不存在！';
                copyWarning.classList.remove('hidden');
                return false;
            }

            // 检查原路径与目标路径是否一致
            if (sourcePath === targetPath) {
                copyWarning.innerHTML = '原路径与目标路径不能一样！';
                copyWarning.classList.remove('hidden');
                return false;
            }

            copyWarning.classList.add('hidden');
            copyInfo.classList.remove('hidden');
            $('#copy-modal').modal('show');
            return true;
        },
        function (data) {
            if (data.status === 0) {
                copyInfo.classList.add('hidden');
                copyWarning.innerHTML = data.message;
                copyWarning.classList.remove('hidden');
            } else {
                location.reload();
            }
        }
    );

    // “移动”按钮的点击事件
    for (let i = 0; i < moveBtnList.length; i++) {
        moveBtnList[i].addEventListener('click', function (e) {
            moveForm.action = this.getAttribute('data-href');
            moveForm.querySelector('#move-source-path').value = this.getAttribute('data-source-path');
            moveForm.querySelector('#new-path').value = '';
            $('#move-modal').modal('show');
        });
    }

    // 移动表单的提交事件
    ajaxSubmitForm(
        'move',
        function (form) {
            // 检查路径中是否包含"\\"
            const sourcePath = form.querySelector('#move-source-path').value.toLowerCase();
            const newPath = form.querySelector('#new-path').value.toLowerCase();
            if (newPath.indexOf('\\') < 0) {
                moveWarning.innerHTML = '路径不存在！';
                moveWarning.classList.remove('hidden');
                return false;
            }

            // 检查原路径和新路径是否相同
            if (sourcePath === newPath) {
                moveWarning.innerHTML = '原路径与新路径不能相同！';
                moveWarning.classList.remove('hidden');
                return false;
            }

            moveWarning.classList.add('hidden');
            moveInfo.classList.remove('hidden');
            $('#move-modal').modal('show');
            return true;
        },
        function (data) {
            if (data.status === 0) {
                moveInfo.classList.add('hidden');
                moveWarning.innerHTML = data.message;
                moveWarning.classList.remove('hidden');
            } else {
                location.reload();
            }
        }
    );

    // “删除”按钮的点击事件
    for (let i = 0; i < removeBtnList.length; i++) {
        removeBtnList[i].addEventListener('click', function (e) {
            document.querySelector('#remove-modal .remove-file-name').innerHTML = fileList.children[Number(this.getAttribute('data-index'))].querySelector('.name a').innerHTML;
            decideRemoveBtn.setAttribute('data-href', this.getAttribute('data-href'));
            $('#remove-modal').modal('show');
        });
    }

    // 删除模态框中的“确定删除”按钮点击事件
    decideRemoveBtn.allowSubmit = true;
    decideRemoveBtn.addEventListener('click', function (e) {
        // 防止提交太快
        if (!decideRemoveBtn.allowSubmit) {
            return undefined;
        }
        decideRemoveBtn.setAttribute('disabled', '');
        decideRemoveBtn.allowSubmit = false;
        removeWarning.classList.add('hidden');
        removeInfo.classList.remove('hidden');

        // 提交表单
        const formData = new FormData();
        ajax.post(this.getAttribute('data-href'), '', function (data) {
            if (data.status === 0) {
                removeInfo.classList.add('hidden');
                removeWarning.innerHTML = data.message;
                removeWarning.classList.remove('hidden');
                decideRemoveBtn.removeAttribute('disabled');
                decideRemoveBtn.allowSubmit = true;
            } else {
                location.reload();
            }
        });
    });

    // 选择文件事件
    uploadFileInput.addEventListener('change', function (e) {
        if (this.files.length <= 0) return undefined;
        const file = this.files[0];
        uploadFileForm.querySelector('.file-input .text').innerText = file.name;
    });

    // 文件上传进度条控制
    function setUploadProgress (value) {
        const bar = uploadFileProgress.querySelector('.progress-bar');
        bar.setAttribute('aria-valuenow', value);
        bar.style.width = value + '%';
        bar.innerHTML = value + '%';
    }

    // 上传文件表单提交
    ajaxUploadFile(
        'upload-file',
        undefined,
        function (value) {
            if (0 < value && value < 100) {
                uploadFileProgress.classList.remove('hidden');
                setUploadProgress(value);
            } else if (value >= 100) {
                setUploadProgress(value);
                uploadInfo.classList.remove('hidden');
            }
        },
        function (data) {
            if (data.status === 0) {
                uploadFileProgress.classList.add('hidden');
                uploadInfo.classList.add('hidden');
                uploadWarning.innerHTML = data.message;
                uploadWarning.classList.remove('hidden');
            } else {
                location.reload();
            }
        }
    );

})(window, document);