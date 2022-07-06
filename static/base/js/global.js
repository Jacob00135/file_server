function ajaxSubmitForm(formSelector, callback) {
    // AJAX代替form标签提交表单
    const form = document.querySelector(formSelector);
    if (form === null || form.nodeName !== 'FORM') {
        return undefined;
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const xhr = new XMLHttpRequest();
        xhr.addEventListener('readystatechange', function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                callback(JSON.parse(xhr.responseText));
            }
        });
        xhr.open('post', form.action, true);
        xhr.send(new FormData(form));
    });
}