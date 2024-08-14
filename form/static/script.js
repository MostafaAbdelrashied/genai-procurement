document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        chatMessages: document.getElementById('chat-messages'),
        userInput: document.getElementById('user-input'),
        sendButton: document.getElementById('send-button'),
        form: document.getElementById('form'),
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

    const URLS = {
        UUID_CONVERT: name => `/uuid/convert-string/${encodeURIComponent(name)}`,
        CREATE_SESSION: uuid => `/sessions/create_session?session_id=${uuid}`,
        GET_SESSION_DATA: uuid => `/sessions/get_session_data/${uuid}`,
        CHAT_MESSAGE: uuid => `/chat/message?session_id=${uuid}`,
        UPDATE_SESSION_FORM: uuid => `/sessions/update_session_form/${uuid}`,
    };

    class UIManager {
        static displayMessage(message, isUser = false) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message', isUser ? 'user-message' : 'bot-message');
            messageElement.textContent = message;
            elements.chatMessages.appendChild(messageElement);
            elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
        }

        static showNotification(message, isError = false) {
            console[isError ? 'error' : 'log'](message);
            this.displayMessage(`${isError ? 'Error' : 'Info'}: ${message}`, false);
        }

        static updateSessionUI(name, uuid) {
            elements.sessionNameInput.style.display = 'none';
            elements.createSessionButton.style.display = 'none';
            const sessionInfoDisplay = document.createElement('div');
            sessionInfoDisplay.innerHTML = `
                <div>Text: ${name}</div>
                <div>UUID: ${uuid}</div>
            `;
            sessionInfoDisplay.classList.add('session-info-display');
            elements.sessionWindow.appendChild(sessionInfoDisplay);
        }

        static showChatInterface() {
            ['chatMessages', 'userInput', 'sendButton', 'formContainer'].forEach(id => {
                elements[id].style.display = 'block';
            });
        }

        static addLoadingIndicator() {
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

            return {
                loadingElement: loadingWrapper,
                stopTimer: () => clearInterval(timerInterval)
            };
        }
    }

    class FormManager {
        static getFormattedData() {
            return {
                general_information: {
                    title: elements.title.value,
                    detailed_description: {
                        business_need: elements.businessNeed.value,
                        project_scope: elements.projectScope.value,
                        type_of_contract: elements.contractType.value
                    }
                },
                financial_details: {
                    start_date: elements.startDate.value,
                    end_date: elements.endDate.value,
                    expected_amount: elements.expectedAmount.value,
                    currency: elements.currency.value
                }
            };
        }

        static updateForm(formData) {
            const generalInfo = formData.general_information || {};
            const financialDetails = formData.financial_details || {};
            const detailedDescription = generalInfo.detailed_description || {};

            elements.title.value = generalInfo.title || '';
            elements.businessNeed.value = detailedDescription.business_need || '';
            elements.projectScope.value = detailedDescription.project_scope || '';
            elements.contractType.value = detailedDescription.type_of_contract || '';
            elements.startDate.value = financialDetails.start_date || '';
            elements.endDate.value = financialDetails.end_date || '';
            elements.expectedAmount.value = financialDetails.expected_amount || '';
            elements.currency.value = financialDetails.currency || '';
        }
    }

    class APIManager {
        static async fetchWithErrorHandling(url, options) {
            try {
                const response = await fetch(url, options);
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'An error occurred');
                }
                return response.json();
            } catch (error) {
                UIManager.showNotification(error.message, true);
                throw error;
            }
        }

        static async createSession(name) {
            const { uuid } = await this.fetchWithErrorHandling(URLS.UUID_CONVERT(name));
            await this.fetchWithErrorHandling(URLS.CREATE_SESSION(uuid), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            });
            return uuid;
        }

        static async fetchFormData(uuid) {
            const data = await this.fetchWithErrorHandling(URLS.GET_SESSION_DATA(uuid));
            return data.form_data;
        }

        static async sendChatMessage(uuid, message) {
            const { response } = await this.fetchWithErrorHandling(URLS.CHAT_MESSAGE(uuid), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });
            return response;
        }

        static async updateForm(uuid, formData) {
            await this.fetchWithErrorHandling(URLS.UPDATE_SESSION_FORM(uuid), {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });
        }
    }

    async function initializeSession() {
        const name = elements.sessionNameInput.value.trim();
        if (!name) {
            UIManager.showNotification('Please enter a session name', true);
            return;
        }

        try {
            sessionUUID = await APIManager.createSession(name);
            UIManager.updateSessionUI(name, sessionUUID);
            UIManager.showChatInterface();
            await fetchAndUpdateForm();
        } catch (error) {
            UIManager.showNotification(`Error creating session: ${error.message}`, true);
        }
    }

    async function fetchAndUpdateForm() {
        if (!sessionUUID) return;

        try {
            const formData = await APIManager.fetchFormData(sessionUUID);
            FormManager.updateForm(formData);
        } catch (error) {
            UIManager.showNotification('Error fetching form data', true);
        }
    }

    async function handleSendMessage() {
        const message = elements.userInput.value.trim();
        if (!message || !sessionUUID) return;

        UIManager.displayMessage(message, true);
        elements.userInput.value = '';

        const { loadingElement, stopTimer } = UIManager.addLoadingIndicator();

        try {
            const response = await APIManager.sendChatMessage(sessionUUID, message);
            UIManager.displayMessage(response);
            await fetchAndUpdateForm();
        } catch (error) {
            UIManager.showNotification('Error processing your message', true);
        } finally {
            stopTimer();
            loadingElement.remove();
        }
    }

    async function handleSaveForm() {
        if (!sessionUUID) return;

        try {
            const formData = FormManager.getFormattedData();
            await APIManager.updateForm(sessionUUID, formData);
            UIManager.showNotification('Form updated successfully');
        } catch (error) {
            UIManager.showNotification('Error updating form', true);
        }
    }

    // Event Listeners
    elements.createSessionButton.addEventListener('click', initializeSession);
    elements.sessionNameInput.addEventListener('keypress', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            initializeSession();
        }
    });
    elements.sendButton.addEventListener('click', handleSendMessage);
    elements.userInput.addEventListener('keypress', event => {
        if (event.key === 'Enter') handleSendMessage();
    });
    elements.refreshFormButton.addEventListener('click', fetchAndUpdateForm);
    elements.saveFormButton.addEventListener('click', event => {
        event.preventDefault();
        handleSaveForm();
    });
});