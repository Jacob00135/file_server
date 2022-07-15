(function (window, document) {
    // AJAX代替表单发送修改密码请求
    const updatePswWarning = document.querySelector('#update-password-warning');
    ajaxSubmitForm(
        'update-password',
        function (form){
            const password = form.querySelector('input[name="password"]').value;
            const againPassword = form.querySelector('input.again-password').value;
            if (password !== againPassword) {
                updatePswWarning.innerHTML = '两次输入的密码不一致！';
                updatePswWarning.classList.remove('hidden');
                return false;
            }
            return true;
        },
        function (data) {
            if (data.status === 0) {
                updatePswWarning.innerHTML = data.message;
                updatePswWarning.classList.remove('hidden');
            } else {
                location.reload();
            }
        }
    );
})(window, document);