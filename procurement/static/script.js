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
        contractType: document.getElementById('contract-type'),
        sourceType: document.getElementById('external-source-type'),
        contractLimit: document.getElementById('external-contract-limit'),
        refreshFormButton: document.getElementById('refresh-form-button'),

        title: document.getElementById('title'),
        businessNeed: document.getElementById('business-need'),
        projectScope: document.getElementById('project-scope'),
        startDate: document.getElementById('start-date'),
        endDate: document.getElementById('end-date'),
        expectedAmount: document.getElementById('expected-amount'),
        currency: document.getElementById('currency'),
    };

    let sessionUUID = null;

    // Constants for URLs
    const URLS = {
        UUID_CONVERT: (name) => `/uuid/convert-string/${encodeURIComponent(name)}`,
        CREATE_SESSION: (uuid) => `/sessions/create_session?session_id=${uuid}`,
        GET_SESSION_DATA: (uuid) => `/sessions/get_session_data/${uuid}`,
        CHAT_MESSAGE: (sessionUUID) => `chat/message?session_id=${sessionUUID}`,
        UPDATE_SESSION_FORM: (sessionUUID) => `/sessions/update_session_form/${sessionUUID}`,
    };

    // Error handling and user feedback
    const showError = (message) => {
        console.error(message);
        addMessage(elements.chatMessages, `Error: ${message}`, false);
    };

    // Helper for fetching and error handling
    const fetchWithErrorHandling = async (url, options) => {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'An error occurred');
            }
            return response.json();
        } catch (error) {
            showError(error.message);
            throw error;
        }
    };

    // Helper functions
    const formatDate = (dateString) => {
        if (!dateString) return '';
        const [year, month, day] = dateString.split('-');
        if (!day || !month || !year) return '';  // Ensure valid date parts
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    };

    const getFormData = (form) => Object.fromEntries(new FormData(form));

    // Updating UI elements
    const updateSessionUI = (elements, name, uuid) => {
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

    const showChatInterface = (elements) => {
        ['chatMessages', 'userInput', 'sendButton', 'formContainer'].forEach((id) => {
            elements[id].style.display = 'block';
        });
    };

    const addMessage = (chatMessages, message, isUser = false) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', isUser ? 'user-message' : 'bot-message');
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const addLoadingIndicator = (chatMessages) => {
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
    };

    const updateForm = (elements, formData) => {
        const {
            title = '',
            ['business-need']: businessNeed = '',
            ['project-scope']: projectScope = '',
            ['contract-type']: contractType = '',
            ['source-type']: sourceType = '',
            ['contract-limit']: contractLimit = '',
            ['start-date']: startDate = '',
            ['end-date']: endDate = '',
            ['expected-amount']: expectedAmount = '',
            currency = ''
        } = formData;

        elements.title.value = title;
        elements.businessNeed.value = businessNeed;
        elements.projectScope.value = projectScope;
        elements.contractType.value = contractType;

        const isExternal = contractType === 'external';
        elements.sourceType.style.display = isExternal ? 'block' : 'none';
        elements.contractLimit.style.display = isExternal ? 'block' : 'none';

        if (isExternal) {
            elements.sourceType.querySelector('select').value = sourceType;
            elements.contractLimit.querySelectorAll('input[type="radio"]').forEach((radio) => {
                radio.checked = radio.value.toLowerCase() === contractLimit.toLowerCase();
            });
        }

        elements.startDate.value = formatDate(startDate);
        elements.endDate.value = formatDate(endDate);
        elements.expectedAmount.value = expectedAmount;
        elements.currency.value = currency;
    };

    const validateForm = (elements) => {
        let isValid = true;
        const requiredFields = [
            elements.title,
            elements.businessNeed,
            elements.projectScope,
            elements.contractType,
            elements.startDate,
            elements.endDate,
            elements.expectedAmount,
            elements.currency,
        ];

        if (elements.contractType.value === 'external') {
            requiredFields.push(elements.sourceType.querySelector('select'));
            const contractLimitSelected = [...elements.contractLimit.querySelectorAll('input[type="radio"]')].some(
                (radio) => radio.checked
            );
            if (!contractLimitSelected) {
                elements.contractLimit.classList.add('invalid');
                isValid = false;
            }
        }

        requiredFields.forEach((field) => {
            if (!field.value) {
                isValid = false;
                field.classList.add('invalid');
            } else {
                field.classList.remove('invalid');
            }
        });

        return isValid;
    };

    const fetchAndUpdateForm = async () => {
        if (!sessionUUID) {
            // showError('No active session');
            return;
        }

        try {
            const data = await fetchWithErrorHandling(URLS.GET_SESSION_DATA(sessionUUID));
            updateForm(elements, data.form_data);
            // console.log('Form updated with data:', data.form_data);
        } catch (error) {
            showError('Error fetching form data');
        }
    };

    const createSession = async () => {
        const name = elements.sessionNameInput.value.trim();
        if (!name) {
            showError('Please enter a session name');
            return;
        }

        try {
            const { uuid } = await fetchWithErrorHandling(URLS.UUID_CONVERT(name));
            sessionUUID = uuid;

            await fetchWithErrorHandling(URLS.CREATE_SESSION(uuid), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            });

            updateSessionUI(elements, name, uuid);
            showChatInterface(elements);
            await fetchAndUpdateForm(); // Fetch and update form data after creating session
        } catch (error) {
            showError(`Error creating session: ${error.message}`);
        }
    };

    const sendMessage = async () => {
        const message = elements.userInput.value.trim();
        if (!message || !sessionUUID) return;

        addMessage(elements.chatMessages, message, true);
        elements.userInput.value = '';

        const { loadingElement, stopTimer } = addLoadingIndicator(elements.chatMessages);

        try {
            const { response: botResponse } = await fetchWithErrorHandling(URLS.CHAT_MESSAGE(sessionUUID), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });

            addMessage(elements.chatMessages, botResponse);
            await fetchAndUpdateForm(); // Ensure form update after chat interaction response
        } catch (error) {
            showError('Error processing your message');
        } finally {
            stopTimer();
            loadingElement.remove();
        }
    };

    const sendFormUpdate = async (formData) => {
        if (!sessionUUID) {
            // showError('No active session');
            return;
        }

        try {
            await fetchWithErrorHandling(URLS.UPDATE_SESSION_FORM(sessionUUID), {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });
            // console.log('Form data sent to server:', formData);
            await fetchAndUpdateForm(); // Fetch updated data from server
        } catch (error) {
            showError('Error updating form');
        }
    };

    const handleFormChange = async (event) => {
        const formData = getFormData(elements.procurementForm);
        await sendFormUpdate(formData);
    };

    // Event Listeners
    elements.createSessionButton.addEventListener('click', createSession);
    elements.sessionNameInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            createSession();
        }
    });

    elements.sendButton.addEventListener('click', sendMessage);
    elements.userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') sendMessage();
    });

    elements.refreshFormButton.addEventListener('click', fetchAndUpdateForm);

    elements.procurementForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (!validateForm(elements)) {
            showError('Form validation failed. Please fill out all required fields.');
            return;
        }

        const formData = getFormData(elements.procurementForm);
        await sendFormUpdate(formData);
    });

    elements.saveFormButton.addEventListener('click', async (event) => {
        event.preventDefault();
        if (!validateForm(elements)) {
            showError('Form validation failed. Please fill out all required fields.');
            return;
        }

        const formData = getFormData(elements.procurementForm);
        await sendFormUpdate(formData);
    });

    elements.contractType.addEventListener('change', ({ target }) => {
        const isExternal = target.value === 'external';
        elements.sourceType.style.display = isExternal ? 'block' : 'none';
        elements.contractLimit.style.display = isExternal ? 'block' : 'none';
    });

    // Add event listeners for form fields
    Object.values(elements).forEach(element => {
        if (element.tagName === 'INPUT' || element.tagName === 'SELECT' || element.tagName === 'TEXTAREA') {
            element.addEventListener('change', handleFormChange);
        }
    });
});