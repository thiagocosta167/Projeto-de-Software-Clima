function showForm(formType) {
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.querySelectorAll('.form').forEach(form => {
        form.classList.add('hidden');
    });

    document.querySelector(`#${formType}Form`).classList.remove('hidden');
    document.querySelector(`button[onclick="showForm('${formType}')"]`).classList.add('active');
}

document.getElementById('signupForm').addEventListener('submit', function(e) {
    const senha = document.querySelector('#signupForm input[name="senha"]').value;
    const confirmarSenha = document.querySelector('#signupForm input[name="confirmar_senha"]').value;
    
    if (senha !== confirmarSenha) {
        e.preventDefault();
        alert('As senhas não coincidem!');
        return false;
    }
});

document.querySelectorAll('.form').forEach(form => {
    form.addEventListener('submit', async function(e) {
        if (form.id === 'signupForm') return;
        
        e.preventDefault();
        const formData = new FormData(form);
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });

            if (response.redirected) {
                window.location.href = response.url;
            } else {
                const result = await response.json();
                if (result.error) {
                    alert(result.error);
                }
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro na conexão com o servidor');
        }
    });
});
