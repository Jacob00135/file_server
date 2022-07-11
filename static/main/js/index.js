(function (window, document) {
    const fileList = document.querySelector('#file-list');
    const typeList = document.querySelectorAll('#file-list > li.list-group-item > .type');
    const fullNameBtnList = document.querySelectorAll('#file-list .show-full-name');
    const downloadBtnList = document.querySelectorAll('#file-list .download-dir');
    const modalDownloadBtn = document.querySelector('#download-modal .download');
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

})(window, document);