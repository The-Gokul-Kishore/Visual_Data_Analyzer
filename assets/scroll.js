document.addEventListener('DOMContentLoaded', function () {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        const observer = new MutationObserver((mutationsList) => {
            mutationsList.forEach((mutation) => {
                if (mutation.addedNodes.length > 0) {
                    // Check if any added node is a user message
                    mutation.addedNodes.forEach((node) => {
                        if (node.classList && node.classList.contains('user-message')) {
                            node.scrollIntoView({ behavior: 'smooth', block: 'end' });
                        }
                    });
                }
            });
        });

        // Observe changes in the child elements of the container
        observer.observe(chatContainer, { childList: true });
    }
});
