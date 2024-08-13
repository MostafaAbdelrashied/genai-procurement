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
        UUID_CONVERT: name => `/uuid/convert-string/${encodeURIComponent(name)}`,
        CREATE_SESSION: uuid => `/sessions/create_session?session_id=${uuid}`,
        GET_SESSION_DATA: uuid => `/sessions/get_session_data/${uuid}`,
        CHAT_MESSAGE: uuid => `/chat/message?session_id=${uuid}`,
        UPDATE_SESSION_FORM: uuid => `/sessions/update_session_form/${uuid}`,
    };

    // UI Update and Helper Functions 

    const showError = message => {
        console.error(message);
        displayMessage(elements.chatMessages, `Error: ${message}`, false);
    };

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

    const getFormData = form => Object.fromEntries(new FormData(form));

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
        ['chatMessages', 'userInput', 'sendButton', 'formContainer'].forEach(id => {
            elements[id].style.display = 'block';
        });
    };

    const displayMessage = (chatMessages, message, isUser = false) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', isUser ? 'user-message' : 'bot-message');
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const addLoadingIndicator = chatMessages => {
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

    const updateForm = formData => {
        const generalInfo = formData["general_information"] || {};
        const financialDetails = formData["financial_details"] || {};
        const detailedDescription = generalInfo["detailed_description"] || {};

        elements.title.value = generalInfo.title || '';
        elements.businessNeed.value = detailedDescription["business_need"] || '';
        elements.projectScope.value = detailedDescription["project_scope"] || '';
        elements.contractType.value = detailedDescription["type_of_contract"] || '';

        elements.startDate.value = financialDetails["start_date"];  // assuming the date is already in yyyy-MM-dd
        elements.endDate.value = financialDetails["end_date"];      // assuming the date is already in yyyy-MM-dd
        elements.expectedAmount.value = financialDetails["expected_amount"] || '';
        elements.currency.value = financialDetails["currency"] || '';
    };

    const validateForm = () => {
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

        requiredFields.forEach(field => {
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
        if (!sessionUUID) return;

        try {
            const data = await fetchWithErrorHandling(URLS.GET_SESSION_DATA(sessionUUID));
            updateForm(data.form_data);
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

            updateSessionUI(name, uuid);
            showChatInterface();
            await fetchAndUpdateForm();
        } catch (error) {
            showError(`Error creating session: ${error.message}`);
        }
    };

    const sendMessage = async () => {
        const message = elements.userInput.value.trim();
        if (!message || !sessionUUID) return;

        displayMessage(elements.chatMessages, message, true);
        elements.userInput.value = '';

        const { loadingElement, stopTimer } = addLoadingIndicator(elements.chatMessages);

        try {
            const { response } = await fetchWithErrorHandling(URLS.CHAT_MESSAGE(sessionUUID), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });

            displayMessage(elements.chatMessages, response);
            await fetchAndUpdateForm();
        } catch (error) {
            showError('Error processing your message');
        } finally {
            stopTimer();
            loadingElement.remove();
        }
    };

    const sendFormUpdate = async formData => {
        if (!sessionUUID) return;

        try {
            await fetchWithErrorHandling(URLS.UPDATE_SESSION_FORM(sessionUUID), {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });
            await fetchAndUpdateForm();
        } catch (error) {
            showError('Error updating form');
        }
    };

    const handleFormChange = async event => {
        const formData = {
            general_information: {
                title: elements.title.value,
                detailed_description: {
                    business_need: elements.businessNeed.value,
                    project_scope: elements.projectScope.value,
                    type_of_contract: elements.contractType.value
                }
            },
            financial_details: {
                start_date: elements.startDate.value,        // yyyy-MM-dd
                end_date: elements.endDate.value,            // yyyy-MM-dd
                expected_amount: elements.expectedAmount.value,
                currency: elements.currency.value
            }
        };
        await sendFormUpdate(formData);
    };

    // Event Listeners 
    elements.createSessionButton.addEventListener('click', createSession);

    elements.sessionNameInput.addEventListener('keypress', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            createSession();
        }
    });

    elements.sendButton.addEventListener('click', sendMessage);
    elements.userInput.addEventListener('keypress', event => {
        if (event.key === 'Enter') sendMessage();
    });

    elements.refreshFormButton.addEventListener('click', fetchAndUpdateForm);

    elements.procurementForm.addEventListener('submit', async event => {
        event.preventDefault();
        if (!validateForm()) {
            showError('Form validation failed. Please fill out all required fields.');
            return;
        }

        const formData = getFormData(elements.procurementForm);
        await sendFormUpdate(formData);
    });

    elements.saveFormButton.addEventListener('click', async event => {
        event.preventDefault();
        if (!validateForm()) {
            showError('Form validation failed. Please fill out all required fields.');
            return;
        }

        const formData = getFormData(elements.procurementForm);
        await sendFormUpdate(formData);
    });

    elements.contractType.addEventListener('change', handleFormChange);

    // Add event listeners for real-time form changes 
    Object.values(elements).forEach(element => {
        if (['INPUT', 'SELECT', 'TEXTAREA'].includes(element.tagName)) {
            element.addEventListener('change', handleFormChange);
        }
    });
});
