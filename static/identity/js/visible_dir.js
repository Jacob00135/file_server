(function(window, document) {
    ajaxSubmitForm('form[name="add-dir"]', function (data) {
        if (data.status === 0) {
            const warning = document.querySelector('#add-dir-warning');
            warning.innerHTML = data.message;
            warning.classList.remove('hidden');
        } else {
            location.reload();
        }
    });
})(window, document);