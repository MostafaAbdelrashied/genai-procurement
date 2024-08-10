document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const schemaContent = document.getElementById('schema-content');
    const sessionWindow = document.getElementById('session-window');
    const sessionNameInput = document.getElementById('session-name');
    const createSessionButton = document.getElementById('create-session-button');

    let menuState = {};
    let sessionUUID = null;

    // Hide chat interface initially
    [chatMessages, userInput, sendButton].forEach(el => el.style.display = 'none');

    const createSession = async () => {
        const name = sessionNameInput.value.trim();
        if (!name) return;

        try {
            const response = await fetch(`/uuid/convert-string/${encodeURIComponent(name)}`);
            if (!response.ok) throw new Error('Failed to convert string to UUID');

            const { uuid } = await response.json();
            sessionUUID = uuid;

            // Update UI
            [sessionNameInput, createSessionButton].forEach(el => el.style.display = 'none');
            const sessionInfoDisplay = document.createElement('div');
            sessionInfoDisplay.innerHTML = `
                <div>Text: ${name}</div>
                <div>UUID: ${sessionUUID}</div>
            `;
            sessionInfoDisplay.classList.add('session-info-display');
            sessionWindow.appendChild(sessionInfoDisplay);

            // Show chat interface
            [chatMessages, userInput, sendButton].forEach(el => el.style.display = 'block');
        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, there was an error creating the session.', false);
        }
    };

    createSessionButton.addEventListener('click', createSession);
    sessionNameInput.addEventListener('keypress', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            createSession();
        }
    });

    function addMessage(message, isUser = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', isUser ? 'user-message' : 'bot-message');
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addLoadingIndicator() {
        const loadingWrapper = document.createElement('div');
        loadingWrapper.innerHTML = `
            <div class="loading-typing">
                <div class="bounce bounce1"></div>
                <div class="bounce bounce2"></div>
                <div class="bounce bounce3"></div>
            </div>
            <span class="loading-timer"></span>
        `;
        loadingWrapper.classList.add('bot-message', 'loading-wrapper');
        chatMessages.appendChild(loadingWrapper);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        const timerElement = loadingWrapper.querySelector('.loading-timer');
        const startTime = Date.now();
        const timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            timerElement.textContent = `${elapsed}s`;
        }, 1000);

        return { loadingElement: loadingWrapper, stopTimer: () => clearInterval(timerInterval) };
    }

    function updateSchema(schema) {
        schemaContent.innerHTML = '';

        function createSchemaItem(key, value, path = '') {
            const schemaItem = document.createElement('div');
            schemaItem.classList.add('schema-item');

            const header = document.createElement('div');
            header.classList.add('schema-header');
            schemaItem.appendChild(header);

            const indicator = document.createElement('span');
            indicator.classList.add('indicator');
            header.appendChild(indicator);

            const title = document.createElement('h3');
            title.textContent = key;
            header.appendChild(title);

            if (typeof value === 'object' && value !== null) {
                title.classList.add('collapsible');
                const content = document.createElement('div');
                content.classList.add('schema-content');

                let filledCount = 0;
                const totalCount = Object.keys(value).length;

                Object.entries(value).forEach(([subKey, subValue]) => {
                    const subItem = createSchemaItem(subKey, subValue, `${path}${key}.`);
                    content.appendChild(subItem);
                    if (subItem.querySelector('.indicator').classList.contains('filled')) {
                        filledCount++;
                    }
                });

                schemaItem.appendChild(content);

                const counter = document.createElement('span');
                counter.classList.add('counter');
                counter.textContent = `(${filledCount}/${totalCount})`;
                header.appendChild(counter);

                const arrow = document.createElement('span');
                arrow.classList.add('arrow');
                arrow.innerHTML = '&#9660;';
                header.appendChild(arrow);

                const itemPath = `${path}${key}`;
                if (menuState[itemPath] === undefined) {
                    menuState[itemPath] = false;
                }

                content.style.display = menuState[itemPath] ? 'block' : 'none';
                if (menuState[itemPath]) header.classList.add('active');

                header.addEventListener('click', () => {
                    header.classList.toggle('active');
                    content.style.display = content.style.display === 'none' ? 'block' : 'none';
                    menuState[itemPath] = !menuState[itemPath];
                });

                indicator.classList.add(filledCount === totalCount ? 'filled' : 'unfilled');
            } else {
                const content = document.createElement('p');
                content.textContent = value;
                schemaItem.appendChild(content);
                indicator.classList.add(value ? 'filled' : 'unfilled');
            }

            return schemaItem;
        }

        Object.entries(schema).forEach(([key, value]) => {
            schemaContent.appendChild(createSchemaItem(key, value));
        });
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message || !sessionUUID) return;

        addMessage(message, true);
        userInput.value = '';

        const { loadingElement, stopTimer } = addLoadingIndicator();

        try {
            const response = await fetch(`chat/message?session_id=${sessionUUID}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const { response: botResponse, form } = await response.json();
            addMessage(botResponse);
            updateSchema(form);
        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, there was an error processing your message.');
        } finally {
            stopTimer();
            loadingElement.remove();
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', event => {
        if (event.key === 'Enter') sendMessage();
    });
});