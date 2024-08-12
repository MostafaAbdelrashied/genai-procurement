document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        chatMessages: document.getElementById('chat-messages'),
        userInput: document.getElementById('user-input'),
        sendButton: document.getElementById('send-button'),
        procurementForm: document.getElementById('procurement-form'),
        saveFormButton: document.getElementById('save-form-button'),
        formContainer: document.getElementById('form-container'),
        sessionWindow: document.getElementById('session-window'),
        sessionNameInput: document.getElementById('session-name'),
        createSessionButton: document.getElementById('create-session-button'),
        contractTypeSelect: document.getElementById('contract-type'),
        externalSourceType: document.getElementById('external-source-type'),
        externalContractLimit: document.getElementById('external-contract-limit'),
        refreshFormButton: document.getElementById('refresh-form-button')
    };

    let sessionUUID = null;

    const createSession = async () => {
        const name = elements.sessionNameInput.value.trim();
        if (!name) return;

        try {
            const response = await fetch(`/uuid/convert-string/${encodeURIComponent(name)}`);
            if (!response.ok) throw new Error('Failed to convert string to UUID');

            const { uuid } = await response.json();
            sessionUUID = uuid;

            updateSessionUI(name, uuid);
            showChatInterface();
            await fetchAndUpdateForm();
        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, there was an error creating the session.', false);
        }
    };

    const updateSessionUI = (name, uuid) => {
        elements.sessionNameInput.style.display = 'none';
        elements.createSessionButton.style.display = 'none';
        const sessionInfoDisplay = document.createElement('div');
        sessionInfoDisplay.innerHTML = `
            <div>Text: ${name}</div>
            <div>UUID: ${uuid}</div>
        `;
        sessionInfoDisplay.classList.add('session-info-display');
        elements.sessionWindow.appendChild(sessionInfoDisplay);
    };

    const showChatInterface = () => {
        [elements.chatMessages, elements.userInput, elements.sendButton, elements.formContainer].forEach(el => el.style.display = 'block');
    };

    const addMessage = (message, isUser = false) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', isUser ? 'user-message' : 'bot-message');
        messageElement.textContent = message;
        elements.chatMessages.appendChild(messageElement);
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    };

    const addLoadingIndicator = () => {
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
        elements.chatMessages.appendChild(loadingWrapper);
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;

        const timerElement = loadingWrapper.querySelector('.loading-timer');
        const startTime = Date.now();
        const timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            timerElement.textContent = `${elapsed}s`;
        }, 1000);

        return { loadingElement: loadingWrapper, stopTimer: () => clearInterval(timerInterval) };
    };

    const formatDate = (dateString) => {
        if (!dateString) return '';
        const [day, month, year] = dateString.split('.');
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    };

    const fetchAndUpdateForm = async () => {
        if (!sessionUUID) return;

        try {
            const response = await fetch(`/sessions/get_session_data/${sessionUUID}`);
            if (!response.ok) throw new Error('Failed to fetch form data from server');

            const data = await response.json();
            updateForm(data.form_data);
        } catch (error) {
            console.error('Error fetching form data:', error);
        }
    };

    const updateForm = (formData) => {
        const generalInfo = formData['General Information'];
        const financialDetails = formData['Financial Details'];
    
        document.getElementById('title').value = generalInfo.Title || '';
        document.getElementById('business-need').value = generalInfo['Detailed description']['Business need'] || '';
        document.getElementById('project-scope').value = generalInfo['Detailed description']['Project scope'] || '';
    
        const contractType = generalInfo['Detailed description']['Type of contract'];
        const contractTypeSelect = document.getElementById('contract-type');
        if (contractTypeSelect) {
            contractTypeSelect.value = contractType;
            const isExternal = contractType === 'external';
            document.getElementById('external-source-type').style.display = isExternal ? 'block' : 'none';
            document.getElementById('external-contract-limit').style.display = isExternal ? 'block' : 'none';
        }
    
        document.getElementById('start-date').value = formatDate(financialDetails['Start Date']);
        document.getElementById('end-date').value = formatDate(financialDetails['End Date']);
        document.getElementById('expected-amount').value = financialDetails['Expected Amount'] || '';
        document.getElementById('currency').value = financialDetails['Currency'] || '';
    };

    const sendMessage = async () => {
        const message = elements.userInput.value.trim();
        if (!message || !sessionUUID) return;

        addMessage(message, true);
        elements.userInput.value = '';

        const { loadingElement, stopTimer } = addLoadingIndicator();

        try {
            const response = await fetch(`chat/message?session_id=${sessionUUID}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const { response: botResponse } = await response.json();
            addMessage(botResponse);

            await fetchAndUpdateForm();
        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, there was an error processing your message.');
        } finally {
            stopTimer();
            loadingElement.remove();
        }
    };

    const sendFormUpdate = async (formData) => {
        if (!sessionUUID) {
            throw new Error('No active session');
        }

        try {
            const response = await fetch(`/sessions/update_session_form/${sessionUUID}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'accept': 'application/json'
                },
                body: JSON.stringify(formData),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update form on server');
            }
            return await response.json();
        } catch (error) {
            console.error('Error updating form:', error);
            throw error;
        }
    };

    const validateForm = () => {
        let isValid = true;
        const requiredFields = [
            'title', 'business-need', 'project-scope', 'contract-type',
            'start-date', 'end-date', 'expected-amount', 'currency'
        ];

        requiredFields.forEach(field => {
            const element = document.getElementById(field);
            if (!element.value) {
                isValid = false;
                element.classList.add('invalid');
            } else {
                element.classList.remove('invalid');
            }
        });

        if (elements.contractTypeSelect.value === 'external') {
            const sourceType = document.getElementById('source-type');
            if (!sourceType.value) {
                isValid = false;
                sourceType.classList.add('invalid');
            } else {
                sourceType.classList.remove('invalid');
            }

            const contractLimits = document.getElementsByName('contract-limit');
            const isAnyContractLimitSelected = Array.from(contractLimits).some(radio => radio.checked);
            if (!isAnyContractLimitSelected) {
                isValid = false;
                elements.externalContractLimit.classList.add('invalid');
            } else {
                elements.externalContractLimit.classList.remove('invalid');
            }
        }

        return isValid;
    };

    elements.createSessionButton.addEventListener('click', createSession);
    elements.sessionNameInput.addEventListener('keypress', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            createSession();
        }
    });
    elements.refreshFormButton.addEventListener('click', fetchAndUpdateForm);
    elements.sendButton.addEventListener('click', sendMessage);
    elements.userInput.addEventListener('keypress', event => {
        if (event.key === 'Enter') sendMessage();
    });

    elements.procurementForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(elements.procurementForm);
        const data = Object.fromEntries(formData);

        try {
            await sendFormUpdate(data);
            addMessage('Form saved successfully!', false);
        } catch (error) {
            addMessage('Error saving form. Please try again.', false);
        }
    });

    elements.saveFormButton.addEventListener('click', async (event) => {
        event.preventDefault();
        if (validateForm()) {
            const formData = new FormData(elements.procurementForm);
            const data = Object.fromEntries(formData);

            try {
                await sendFormUpdate(data);
                addMessage('Form saved successfully!', false);
            } catch (error) {
                addMessage(`Error saving form: ${error.message}`, false);
            }
        } else {
            addMessage('Please fill in all required fields.', false);
        }
    });

    elements.contractTypeSelect.addEventListener('change', event => {
        const isExternal = event.target.value === 'external';
        elements.externalSourceType.style.display = isExternal ? 'block' : 'none';
        elements.externalContractLimit.style.display = isExternal ? 'block' : 'none';
    });
});