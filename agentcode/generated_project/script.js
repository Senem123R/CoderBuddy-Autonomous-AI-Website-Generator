(() => {
    // --------------------------------------------------
    // Element References & State
    // --------------------------------------------------
    /** @type {HTMLElement|null} */
    const display = document.getElementById('display');
    /** @type {NodeListOf<HTMLElement>} */
    const buttons = document.querySelectorAll('.btn');

    let currentInput = '';
    let previousValue = null; // number
    let operator = null; // '+', '-', '*', '/' or null
    let resetDisplay = false; // flag to clear currentInput on next digit entry

    // --------------------------------------------------
    // Utility Functions
    // --------------------------------------------------
    /**
     * Update the calculator display.
     * Works with both <input> and <div> elements.
     * @param {string|number} value
     */
    function updateDisplay(value) {
        if (!display) return;
        if (display instanceof HTMLInputElement) {
            display.value = String(value);
        } else {
            display.textContent = String(value);
        }
    }

    /**
     * Reset all state and clear the display.
     */
    function clearAll() {
        currentInput = '';
        previousValue = null;
        operator = null;
        resetDisplay = false;
        updateDisplay('0');
    }

    /**
     * Perform a basic arithmetic operation.
     * Returns a number or the string 'Error' for invalid operations.
     * @param {number|string} a
     * @param {number|string} b
     * @param {string} op
     * @returns {number|string}
     */
    function calculate(a, b, op) {
        const numA = typeof a === 'number' ? a : parseFloat(a);
        const numB = typeof b === 'number' ? b : parseFloat(b);
        if (isNaN(numA) || isNaN(numB)) return 'Error';
        switch (op) {
            case '+':
                return numA + numB;
            case '-':
                return numA - numB;
            case '*':
                return numA * numB;
            case '/':
                if (numB === 0) return 'Error';
                return numA / numB;
            default:
                return 'Error';
        }
    }

    /**
     * Handle button click event.
     * @param {Event} event
     */
    function handleButtonClick(event) {
        const target = event.target;
        const value = target.dataset.value;
        if (value === 'C') {
            clearAll();
        } else if (['+', '-', '*', '/'].includes(value)) {
            if (currentInput !== '') {
                previousValue = parseFloat(currentInput);
                operator = value;
                resetDisplay = true;
                currentInput = '';
            }
        } else if (value === '=') {
            if (previousValue !== null && operator !== null && currentInput !== '') {
                const result = calculate(previousValue, currentInput, operator);
                if (result === 'Error') {
                    updateDisplay('Error');
                } else {
                    updateDisplay(result);
                    previousValue = null;
                    operator = null;
                    currentInput = String(result);
                }
            }
        } else {
            if (resetDisplay) {
                currentInput = '';
                resetDisplay = false;
            }
            currentInput += value;
            updateDisplay(currentInput);
        }
    }

    // --------------------------------------------------
    // Event Listeners
    // --------------------------------------------------
    buttons.forEach(button => {
        button.addEventListener('click', handleButtonClick);
    });

    // Initialize display
    updateDisplay('0');
})();