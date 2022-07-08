(function(window, document) {
    const addDirBtn = document.querySelector('#action button[data-target="#add_dir"]');
    const deleteBtn = document.querySelector('#delete-dir-btn');
    const updateBtn = document.querySelector('#update-access-btn');
    const allInvert = document.querySelector('#all-invert-group');
    const dirList = document.querySelector('#dir_list');
    const checkboxList = document.querySelectorAll('#dir_list input[type="checkbox"]');
    const allSelectBtn = document.querySelector('#all-invert-group input[type="checkbox"]');
    const dirItemList = document.querySelectorAll('#dir_list > li.list-group-item');
    const invertBtn = document.querySelector('#all-invert-group .invert-btn');
    const decideDeleteBtn = document.querySelector('#decide-delete-btn');
    const decideUpdateBtn = document.querySelector('#decide-update-btn');
    const accessButtonList = document.querySelectorAll('#dir_list button[data-access]');
    const actionBtnList = [addDirBtn, deleteBtn, updateBtn];

    // ajax代替发送添加路径的表单
    ajaxSubmitForm('add-dir', undefined, function (data) {
        if (data.status === 0) {
            const warning = document.querySelector('#add-dir-warning');
            warning.innerHTML = data.message;
            warning.classList.remove('hidden');
        } else {
            location.reload();
        }
    });

    // “确定删除”按钮点击事件
    decideDeleteBtn.addEventListener('click', function (e) {
        // 获取需要提交的数据
        const dirPathList = [];
        for (let i = 0; i < checkboxList.length; i++) {
            let checkbox = checkboxList[i];
            if (checkbox.checked) {
                dirPathList.push(checkbox.value);
            }
        }

        // 检查数据
        if (dirPathList.length === 0) {
            showWarningModal('未选择要删除的目录！');
            return undefined;
        }

        // ajax提交要删除的目录
        const formData = new FormData();
        formData.append('dir_path_list', JSON.stringify(dirPathList));
        ajax.post(dirList.getAttribute('data-delete-action'), formData, function (data) {
            if (data.status === 0) {
                showWarningModal(data.message);
            } else {
                location.reload();
            }
        });
    });

    // “删除”按钮点击事件
    deleteBtn.selectStatus = false;
    deleteBtn.addEventListener('click', function (e) {
        if (deleteBtn.selectStatus) {
            // 显示其他操作的按钮
            for (let i = 0; i < actionBtnList.length; i++) {
                let btn = actionBtnList[i];
                if (btn !== deleteBtn) {
                    btn.classList.remove('hidden');
                }
            }

            // 按钮状态改变
            deleteBtn.selectStatus = false;

            // 按钮文本改变、背景色改变
            this.innerHTML = '删除';
            this.classList.remove('btn-default')
            this.classList.add('btn-danger')

            // 隐藏“确定删除”按钮
            decideDeleteBtn.classList.add('hidden');

            // 隐藏全选、反选按钮
            allInvert.classList.add('hidden');

            // 隐藏条目复选框
            dirList.classList.remove('select-status');

            // 取消勾选所有条目
            for (let i = 0; i < checkboxList.length; i++) {
                let checkbox = checkboxList[i];
                if (checkbox.checked) {
                    checkbox.click();
                }
            }

            // 取消注册条目中li、span标签的点击事件
            for (let i = 0; i < dirItemList.length; i++) {
                let li = dirItemList[i];
                li.removeEventListener('click', clickDirItem);
            }
        } else {
            // 隐藏其他操作的按钮
            for (let i = 0; i < actionBtnList.length; i++) {
                let btn = actionBtnList[i];
                if (btn !== deleteBtn) {
                    btn.classList.add('hidden');
                }
            }

            // 按钮状态改变
            deleteBtn.selectStatus = true;

            // 按钮文本改变、背景色改变
            this.innerHTML = '取消';
            this.classList.remove('btn-danger')
            this.classList.add('btn-default')

            // 显示“确定删除”按钮
            decideDeleteBtn.classList.remove('hidden');

            // 显示全选、反选按钮
            allInvert.classList.remove('hidden');

            // 显示条目复选框
            dirList.classList.add('select-status');

            // 取消勾选所有条目
            for (let i = 0; i < checkboxList.length; i++) {
                let checkbox = checkboxList[i];
                if (checkbox.checked) {
                    checkbox.click();
                }
            }

            // 注册条目中li、span标签的点击事件
            for (let i = 0; i < dirItemList.length; i++) {
                let li = dirItemList[i];
                li.addEventListener('click', clickDirItem);
            }
        }
    });

    // 条目中复选框状态改变事件
    for (let i = 0; i < checkboxList.length; i++) {
        let checkbox = checkboxList[i];
        checkbox.addEventListener('change', function (e) {
            if (checkbox.checked) {
                // 背景色变红
                dirList.children[i].classList.add('selected');

                // 检查是否已经全选，若已经全选，则勾选全选按钮
                let allSelected = true;
                for (let j = 0; j < checkboxList.length; j++) {
                    if (!checkboxList[j].checked) {
                        allSelected = false;
                        break;
                    }
                }
                if (allSelected) {
                    allSelectBtn.checked = true;
                }
            } else {
                // 背景色取消红色
                dirList.children[i].classList.remove('selected');

                // 取消勾选全选按钮
                allSelectBtn.checked = false;
            }
        });
    }

    // 全选复选框状态改变事件
    allSelectBtn.addEventListener('change', function (e) {
        if (!this.checked) {
            // 取消勾选所有条目的复选框
            for (let i = 0; i < checkboxList.length; i++) {
                let check = checkboxList[i];
                if (check.checked) {
                    checkboxList[i].click();
                }
            }
        } else{
            // 勾选所有条目的复选框
            for (let i = 0; i < checkboxList.length; i++) {
                let check = checkboxList[i];
                if (!check.checked) {
                    checkboxList[i].click();
                }
            }
        }
    });

    // 反选按钮点击事件
    invertBtn.addEventListener('click', function (e) {
        for (let i = 0; i < checkboxList.length; i++) {
            checkboxList[i].click();
        }
    });

    // 条目中的li、span标签的点击事件
    function clickDirItem (e) {
        const target = e.target;
        if (target.nodeName === 'LI' || target.nodeName === 'SPAN') {
            this.querySelector('input[type="checkbox"]').click();
        }
    }

    // “更改权限”按钮点击事件
    updateBtn.updateStatus = false;
    updateBtn.addEventListener('click', function (e) {
        // 初始化权限状态
        for (let i = 0; i < dirList.children.length; i++) {
            let li = dirList.children[i];
            let sourceAccess = Number(li.getAttribute('data-source-access'));
            li.setAttribute('data-access', sourceAccess);
            if (sourceAccess === 1) {
                li.querySelector('.glyphicon.glyphicon-user').classList.add('hidden');
            } else {
                li.querySelector('.glyphicon.glyphicon-user').classList.remove('hidden');
            }
        }

        if (updateBtn.updateStatus) {
            // 显示其他操作的按钮
            for (let i = 0; i < actionBtnList.length; i++) {
                let btn = actionBtnList[i];
                if (btn !== updateBtn) {
                    btn.classList.remove('hidden');
                }
            }

            // 按钮状态改变
            updateBtn.updateStatus = false;

            // 隐藏“确定更改”按钮
            decideUpdateBtn.classList.add('hidden');

            // 此按钮文本改变、背景色改变
            this.innerHTML = '更改权限'
            this.classList.remove('btn-default');
            this.classList.add('btn-primary');

            // 显示所有条目的更改权限按钮
            dirList.classList.remove('update-status');
        } else {
            // 隐藏其他操作的按钮
            for (let i = 0; i < actionBtnList.length; i++) {
                let btn = actionBtnList[i];
                if (btn !== updateBtn) {
                    btn.classList.add('hidden');
                }
            }

            // 按钮状态改变
            updateBtn.updateStatus = true;

            // 显示“确定更改”按钮
            decideUpdateBtn.classList.remove('hidden');

            // 此按钮文本改变、背景色改变
            this.innerHTML = '取消'
            this.classList.remove('btn-primary');
            this.classList.add('btn-default');

            // 显示所有条目的更改权限按钮
            dirList.classList.add('update-status');
        }
    });

    // 权限按钮的点击事件
    for (let i = 0; i < accessButtonList.length; i++) {
        let btn = accessButtonList[i];
        btn.addEventListener('click', function (e) {
            const access = Number(btn.getAttribute('data-access'));
            const li = dirList.children[btn.getAttribute('data-index')];
            li.setAttribute('data-access', access);
            if (access === 1) {
                li.querySelector('.glyphicon.glyphicon-user').classList.add('hidden');
            } else if (access === 4) {
                li.querySelector('.glyphicon.glyphicon-user').classList.remove('hidden');
            }
        });
    }

    // “确定更改”按钮点击事件
    decideUpdateBtn.addEventListener('click', function (e) {
        // 获取数据
        const sendData = [];
        for (let i = 0; i < dirList.children.length; i++) {
            let li = dirList.children[i];
            let sourceAccess = li.getAttribute('data-source-access');
            let access = li.getAttribute('data-access');
            if (sourceAccess !== access) {
                sendData.push({
                    'dir_path': li.querySelector('.text').innerHTML,
                    'access': Number(access)
                })
            }
        }

        // 检查是否有更改
        if (sendData.length === 0) {
            showWarningModal('权限未作任何更改');
            return undefined;
        }

        // 发送更改权限请求
        const formData = new FormData();
        formData.append('update_item', JSON.stringify(sendData))
        ajax.post(dirList.getAttribute('data-update-access-action'), formData, function (data) {
            if (data.status === 0) {
                showWarningModal(data.message);
            } else {
                location.reload();
            }
        });
    });

})(window, document);