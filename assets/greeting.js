// assets/greeting.js

// Esta função garante que o script só rode depois que a página carregar
function initializeGreeting() {
    // Encontra no HTML o elemento que vai mostrar a mensagem
    const greetingElement = document.getElementById('greeting-message');
    
    // Só continua se o elemento existir na página atual
    if (greetingElement) {
        const now = new Date();
        const hour = now.getHours();
        // Formata a hora para o padrão brasileiro (HH:MM)
        const timeString = now.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        let greetingText = '';

        if (hour >= 5 && hour < 12) {
            greetingText = 'Bom dia';
        } else if (hour >= 12 && hour < 18) {
            greetingText = 'Boa tarde';
        } else {
            greetingText = 'Boa noite';
        }
        
        // Define o texto final no elemento
        greetingElement.innerText = `${greetingText}  |  ${timeString}`;
    }
}

// O Dash pode trocar o conteúdo da página dinamicamente.
// Para garantir que a saudação apareça sempre que o menu for carregado,
// usamos um MutationObserver para "observar" mudanças na página.
const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
        if (mutation.type === 'childList') {
            // Se algo mudou na página, tenta rodar a função de saudação
            initializeGreeting();
        }
    }
});

// Começa a observar o corpo do documento
observer.observe(document.body, { childList: true, subtree: true });

// Roda a função uma vez no carregamento inicial
initializeGreeting();
