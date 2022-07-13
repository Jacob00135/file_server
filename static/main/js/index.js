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
    const iconfontMap = {
        'dir': 'glyphicon-folder-open',
        'text': 'glyphicon-file',
        'image': 'glyphicon-picture',
        'audio': 'glyphicon-music',
        'video': 'glyphicon-film',
        'package': 'glyphicon-compressed',
        'other': 'glyphicon-question-sign'
    };

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

})(window, document);