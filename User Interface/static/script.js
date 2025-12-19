document.addEventListener('DOMContentLoaded', () => {

    const screenText = document.getElementById('screen-text');
    const inputContainer = document.getElementById('input-line-container');
    const inputPrompt = document.getElementById('input-prompt');
    const inputLine = document.getElementById('input-line');
    const keypad = document.getElementById('keypad');
    const sideButtons = document.querySelectorAll('.screen-button');
    const cardElement = document.getElementById('card-element');
    const loadingOverlay = document.getElementById('loading-overlay');

    let appState = 'INIT';
    let inputBuffer = '';
    let inputMasked = false;
    let currentUserData = null;
    let currentTerms = {};
    let appConfig = {};
    let typingTimer;
    let tempStorage = {};
    let currentWithdrawalAmount = 0;

    const sounds = {
        cardInsert: new Audio('/static/sounds/card-insert.mp3'),
        cardEject: new Audio('/static/sounds/card-eject.mp3'),
        buttonBeep: new Audio('/static/sounds/button-beep.mp3'),
        buttonClick: new Audio('/static/sounds/button-click.mp3'),
        success: new Audio('/static/sounds/success.mp3'),
        error: new Audio('/static/sounds/error.mp3'),
        cashDispense: new Audio('/static/sounds/cash-dispense.mp3'),
        processing: new Audio('/static/sounds/processing.mp3'),
        receiptPrint: new Audio('/static/sounds/receipt-print.mp3')
    };

    Object.values(sounds).forEach(sound => {
        sound.volume = 0.5; 
    });

    function playSound(soundName) {
        const sound = sounds[soundName];
        if (sound) {
            sound.currentTime = 0;
            sound.play().catch(err => console.log('Sound play failed:', err));
        }
    }

    const RANDOM_NAMES = [
        'Budi Setiawan', 'Siti Aminah', 'Agus Wijaya', 'Dewi Lestari',
        'Eko Prasetyo', 'Rina Marlina', 'Joko Susilo', 'Fitri Handayani',
        'Andi Pratama', 'Putri Ayu'
    ];

    function roundToStep(value, step) {
        const multiplier = 1000000; 
        const valueInt = Math.round(value * multiplier);
        const stepInt = Math.round(step * multiplier);
        const roundedInt = Math.round(valueInt / stepInt) * stepInt;
        return roundedInt / multiplier;
}

    function showLoading(show) {
        if (show) {
            loadingOverlay.classList.remove('hidden');
        } else {
            loadingOverlay.classList.add('hidden');
        }
    }

    async function apiCall(endpoint, method = 'GET', body = null) {
        showLoading(true);
        playSound('processing');
        try {
            const options = {
                method: method,
                headers: { 'Content-Type': 'application/json' },
            };
            if (body) {
                options.body = JSON.stringify(body);
            }
            const response = await fetch(endpoint, options);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Call Error:', error);
            showScreen('KONEKSI GAGAL\nSilakan coba lagi nanti.');
            return null;
        } finally {
            showLoading(false);
        }
    }

    function typingEffect(text, onComplete = null) {
        clearTimeout(typingTimer);
        screenText.innerHTML = '';

        if (typeof text !== 'string') {
            console.warn("typingEffect received non-string:", text);
            text = "Error: Teks tidak valid";
        }

        let i = 0;
        const delay = 10;

        function type() {
            if (i < text.length) {
                if (text.charAt(i) === '\n') {
                    screenText.innerHTML += '<br>';
                } else {
                    screenText.innerHTML += text.charAt(i);
                }
                i++;
                typingTimer = setTimeout(type, delay);
            } else {
                if (onComplete) {
                    onComplete();
                }
            }
        }
        type();
    }

    function setupInput(prompt = '', masked = false) {
        inputBuffer = '';
        inputMasked = masked;
        inputContainer.style.display = 'flex';
        inputPrompt.textContent = prompt;
        updateInputDisplay();
    }

    function hideInput() {
        inputContainer.style.display = 'none';
        inputBuffer = '';
    }

    function updateInputDisplay() {
        if (inputMasked) {
            inputLine.textContent = '*'.repeat(inputBuffer.length);
        } else {
            inputLine.textContent = inputBuffer;
        }
    }

    function showScreen(text, sideButtonOptions = {}, onComplete = null) {
        hideInput();

        sideButtons.forEach(btn => {
            btn.textContent = '';
            btn.onclick = null;
            btn.style.visibility = 'hidden';
        });

        ['l1', 'l2', 'l3', 'l4'].forEach((id, index) => {
            if (sideButtonOptions[id]) {
                const btn = document.getElementById(`btn-${id}`);
                btn.textContent = sideButtonOptions[id].text;
                btn.onclick = () => {
                    playSound('buttonClick'); 
                    sideButtonOptions[id].action();
                };
                btn.style.visibility = 'visible';
            }
        });

        ['r1', 'r2', 'r3', 'r4'].forEach((id, index) => {
            if (sideButtonOptions[id]) {
                const btn = document.getElementById(`btn-${id}`);
                btn.textContent = sideButtonOptions[id].text;
                btn.onclick = () => {
                    playSound('buttonClick'); 
                    sideButtonOptions[id].action();
                };
                btn.style.visibility = 'visible';
            }
        });

        typingEffect(text, onComplete);
    }

    function formatCurrencyJS(angka, kode_mata_uang) {
        if (kode_mata_uang === 'IDR') {
            return `Rp${new Intl.NumberFormat('id-ID').format(angka)}`;
        }

        let options = {
            style: 'decimal',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        };

        if (kode_mata_uang === 'JPY' || kode_mata_uang === 'KRW') {
            options.minimumFractionDigits = 0;
            options.maximumFractionDigits = 0;
        }

        return `${kode_mata_uang} ${new Intl.NumberFormat('en-US', options).format(angka)}`;
    }

    function showReceipt(receiptText, nextState) {
        sideButtons.forEach(btn => {
            btn.textContent = '';
            btn.onclick = null;
            btn.style.visibility = 'hidden';
        });
        
        const successMsg = currentTerms['transaksi_berhasil'] + '\n\n' + 
                        'Struk sedang dicetak...\n' +
                        'Receipt is being printed...\n\n' +
                        'Silakan ambil struk Anda\n' +
                        'Please take your receipt';
        
        typingEffect(successMsg, () => {
            printReceipt(receiptText);

            setTimeout(() => {
                const btn = document.getElementById('btn-r4');
                btn.textContent = 'AMBIL\n/ TAKE';
                btn.onclick = () => {
                    playSound('buttonClick');
                    collectReceipt();
                    setTimeout(() => {
                        handleStateChange(nextState);
                    }, 1000);
                };
                btn.style.visibility = 'visible';
            }, 2500);
        });
    }

    function printReceipt(receiptText) {
        const receiptContainer = document.getElementById('receipt-container');
        const receiptContent = typeof receiptText === 'string' ? receiptText : receiptText.join('\n');
        receiptContainer.innerHTML = '';
        const receiptPaper = document.createElement('div');
        receiptPaper.className = 'receipt-paper';
        receiptPaper.textContent = receiptContent;
        
        receiptPaper.addEventListener('click', function(e) {
            e.stopPropagation();
            playSound('buttonClick');
            openReceiptModal(receiptContent);
        });
        
        receiptPaper.title = 'Klik untuk melihat detail / Click to view details';
        
        receiptContainer.appendChild(receiptPaper);
        setTimeout(() => {
            playSound('receiptPrint');
            receiptPaper.classList.add('printing');
        }, 500);
    }

    function collectReceipt() {
        const receiptPapers = document.querySelectorAll('.receipt-paper');
        receiptPapers.forEach((paper, index) => {
            setTimeout(() => {
                paper.classList.add('collected');
                setTimeout(() => {
                    paper.remove();
                }, 1500);
            }, index * 100);
        });
    }

    function openReceiptModal(receiptText) {
        const modal = document.getElementById('receipt-modal');
        const modalText = document.getElementById('receipt-modal-text');
        
        modalText.textContent = receiptText;
        modal.classList.add('active');
        
        document.body.style.overflow = 'hidden';
    }

    window.closeReceiptModal = function() {
        const modal = document.getElementById('receipt-modal');
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }

    document.addEventListener('click', function(e) {
        const modal = document.getElementById('receipt-modal');
        if (e.target === modal) {
            closeReceiptModal();
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeReceiptModal();
        }
    });

    function animateCardIn() {
        playSound('cardInsert');
        cardElement.classList.remove('ejected');
        cardElement.classList.add('inserted');
        setTimeout(() => {
            handleStateChange('WELCOME');
        }, 1500);
    }

    function animateCardOut() {
        playSound('cardEject');
        cardElement.classList.remove('inserted');
        cardElement.classList.add('ejected');
        setTimeout(() => {
            handleStateChange('INIT');
        }, 1500);
    }

    function handleKeypadInput(key) {
        if (appState === 'INIT') {
            if (key === 'enter') {
                playSound('buttonBeep');
                handleStateChange('CARD_INSERTING');
            }
            return;
        }

        switch (key) {
            case 'enter':
                playSound('buttonBeep');
                processEnterKey();
                break;
            case 'cancel':
                playSound('buttonBeep');
                processCancelKey();
                break;
            case 'clear':
                playSound('buttonBeep');
                inputBuffer = '';
                updateInputDisplay();
                break;
            default: // Angka 0-9 atau .
                if (inputContainer.style.display === 'flex') {
                    playSound('buttonBeep');
                    const isPinInput = appState === 'PIN_LOGIN' ||
                                       appState === 'CHANGE_PIN_OLD' ||
                                       appState === 'CHANGE_PIN_NEW' ||
                                       appState === 'CHANGE_PIN_CONFIRM';

                    if (isPinInput && inputBuffer.length >= 6) {
                        return;
                    }

                    if (key === '.') {
                        if (appState !== 'WITHDRAW_NON_IDR_OTHER') {
                            return;
                        }
                        if (inputBuffer.includes('.')) {
                            return;
                        }
                    }

                    inputBuffer += key;
                    updateInputDisplay();
                }
                break;
        }
    }

    function processEnterKey() {
        const currentInput = inputBuffer;
        inputBuffer = '';

        switch (appState) {
            case 'PIN_LOGIN':
                doLogin(currentInput);
                break;
            case 'TRANSFER_IDR_REK':
                tempStorage.rek_tujuan = currentInput;
                const randomIndex = Math.floor(Math.random() * RANDOM_NAMES.length);
                tempStorage.nama_penerima = RANDOM_NAMES[randomIndex];
                handleStateChange('TRANSFER_IDR_AMOUNT');
                break;
            case 'PAYMENT_PHONE_INPUT':
                tempStorage.nomor_hp = currentInput;
                handleStateChange('PAYMENT_PHONE_NOMINAL');
                break;
            case 'WITHDRAW_IDR_OTHER':
                doWithdrawIDR(currentInput);
                break;
            case 'WITHDRAW_NON_IDR_OTHER':
                doWithdrawNonIDR(currentInput); 
                break;
            case 'PAYMENT_ELECTRICITY_INPUT':
                tempStorage.nomor_meter = currentInput;
                handleStateChange('PAYMENT_ELECTRICITY_NOMINAL');
                break;
            case 'PAYMENT_WATER_INPUT':
                tempStorage.nomor_pelanggan = currentInput;
                doPaymentWaterCheck(currentInput);
                break;
            case 'CHANGE_PIN_OLD':
                tempStorage.pin_lama = currentInput;
                handleStateChange('CHANGE_PIN_NEW');
                break;
            case 'CHANGE_PIN_NEW':
                tempStorage.pin_baru = currentInput;
                handleStateChange('CHANGE_PIN_CONFIRM');
                break;
            case 'CHANGE_PIN_CONFIRM':
                tempStorage.pin_konfirmasi = currentInput;
                doChangePin();
                break;
            case 'TRANSFER_IDR_AMOUNT':
                tempStorage.amount = currentInput;
                handleStateChange('TRANSFER_IDR_CONFIRM');
                break;
            case 'PAYMENT_PHONE_OTHER':
                tempStorage.amount = currentInput;
                handleStateChange('PAYMENT_PHONE_CONFIRM');
                break;
        }
    }

    function processCancelKey() {
        hideInput();
        tempStorage = {};

        if (currentUserData) {
            if (currentUserData.mata_uang_utama === 'IDR') {
                handleStateChange('MAIN_MENU_IDR');
            } else {
                handleStateChange('MAIN_MENU_NON_IDR');
            }
        } else {
            handleStateChange('WELCOME');
        }
    }

    keypad.addEventListener('click', (e) => {
        if (e.target.classList.contains('keypad-btn') && !e.target.disabled) {
            handleKeypadInput(e.target.dataset.key);
        }
    });

    async function initializeApp() {
        const data = await apiCall('/api/status');
        if (data) {
            currentTerms = data.terms;
            appConfig = data.config;

            if (data.logged_in) {
                currentUserData = data.user_data;
                cardElement.classList.add('inserted');
                handleStateChange('WELCOME');
            } else {
                handleStateChange('INIT');
            }
        }
    }

    async function setLanguage(lang) {
        const data = await apiCall('/api/set_language', 'POST', { lang: lang });
        if (data && data.success) {
            currentTerms = data.terms;
            handleStateChange('PIN_LOGIN');
        }
    }

    async function doLogin(pin) {
        const data = await apiCall('/api/login', 'POST', { pin: pin });
        if (data) {
            hideInput();
            if (data.success) {
                playSound('success');
                currentUserData = data.user_data;
                showScreen(data.message, {}, () => {
                    if (currentUserData.mata_uang_utama === 'IDR') {
                        handleStateChange('MAIN_MENU_IDR');
                    } else {
                        handleStateChange('MAIN_MENU_NON_IDR');
                    }
                });
            } else {
                playSound('error')
                if (data.blocked) {
                    showScreen(data.message, {}, () => {
                        setTimeout(handleStateChange, 3000, 'CARD_EJECTING');
                    });
                } else {
                    showScreen(data.message, {}, () => {
                        setTimeout(handleStateChange, 2000, 'PIN_LOGIN');
                    });
                }
            }
        }
    }

    async function doCheckBalance() {
        const data = await apiCall('/api/get_balance');
        if(data && data.success) {
            let text = data.message;
            const lang = currentUserData.bahasa || 'id';
            const backButtonText = lang === 'id' ? 'KEMBALI / BACK' : 'KEMBALI / BACK';

            let options = {
                r4: { text: backButtonText, action: () => handleStateChange(currentUserData.mata_uang_utama === 'IDR' ? 'MAIN_MENU_IDR' : 'MAIN_MENU_NON_IDR') }
            };

            if (data.saldo_idr_ekuivalen) {
                const yesButtonText = lang === 'id' ? 'YA / YES' : 'YA / YES';
                text += `\n\n${currentTerms['saldo_dalam_idr_tanya']}`;
                options.r1 = { text: yesButtonText, action: () => {
                    showScreen(`${currentTerms['saldo_rekening_anda']}\n${data.saldo_utama}\n\n${currentTerms['saldo_dalam_idr_label']}:\n${data.saldo_idr_ekuivalen}`, {
                    r4: { text: backButtonText, action: () => handleStateChange('MAIN_MENU_NON_IDR') }
                    });
                }};
            }
            showScreen(text, options);
        }
    }

    async function doWithdrawIDR(amount) {
        const data = await apiCall('/api/withdraw/idr', 'POST', { amount: amount });
        if (data) {
            hideInput();
            if (data.success) {
                const balanceStr = data.new_balance;          
                const cleanBalance = balanceStr
                    .replace('Rp', '')                         
                    .replace(/\./g, '')                        
                    .trim();                                   
                currentUserData.saldo = parseFloat(cleanBalance);
                if (amount % 50000 === 0 && amount % 100000 !== 0) {
                dispenseCash('50k', amount);
            } else if (amount % 100000 === 0) {
                showDenominationChoice(amount);
            } else {
                showScreen('Jumlah penarikan tidak valid / Invalid withdrawal amount', {}, () => {
                    setTimeout(handleStateChange, 2000, 'WITHDRAW_IDR_MENU');
                });
            }
            } else {
                playSound('error');
                showScreen(data.message, {}, () => {
                    setTimeout(handleStateChange, 3000, 'WITHDRAW_IDR_MENU');
                });
            }
        }
    }

    async function doWithdrawNonIDR(amount_curr) {
        const data = await apiCall('/api/withdraw/non_idr', 'POST', { amount: amount_curr });
        if (data) {
            hideInput();
            if (data.success) {
                const ccyCode = currentUserData.mata_uang_utama;
                const balanceStr = data.new_balance;
                const balanceNum = parseFloat(balanceStr.replace(/[^\d.-]/g, ''));
                currentUserData.saldo = balanceNum;
                const kurs = appConfig.kurs_beli[currentUserData.mata_uang_utama];
                const amountIDR = Math.floor(amount_curr * kurs);
                const roundedTo50k = Math.round(amountIDR / 50000) * 50000;
                const roundedTo100k = Math.round(amountIDR / 100000) * 100000;
                const tolerance = amountIDR * 0.01;
                const isClose50k = Math.abs(amountIDR - roundedTo50k) <= tolerance;
                const isClose100k = Math.abs(amountIDR - roundedTo100k) <= tolerance;
                
                if (isClose100k) {
                        showDenominationChoice(amountIDR);
                    
                } else if (isClose50k) {
                        dispenseCash('50k', roundedTo50k); 
                }else {
                    showScreen('Jumlah penarikan tidak valid / Invalid withdrawal amount', {}, () => {
                        setTimeout(handleStateChange, 2000, 'WITHDRAW_NON_IDR_MENU');
                    });
                }
            } else {
                playSound('error');
                if (data.message === currentTerms['masukkan_angka_valid']) {
                    showScreen(data.message, {}, () => {
                        setTimeout(handleStateChange, 2000, 'WITHDRAW_NON_IDR_OTHER');
                    });
                } else {
                    showScreen(data.message, {}, () => {
                        setTimeout(handleStateChange, 3000, 'WITHDRAW_NON_IDR_MENU');
                    });
                }
            }
        }
    }

    async function doTransferIDR() {
        const transferData = {
            rek_tujuan: tempStorage.rek_tujuan,
            nama_penerima: tempStorage.nama_penerima,
            amount: tempStorage.amount
        };
        const data = await apiCall('/api/transfer/idr', 'POST', transferData);
        if (data) {
            hideInput();
            tempStorage = {};
            if (data.success) {
                playSound('success');
                showReceipt(data.receipt, 'ASK_CONTINUE');
            } else {
                playSound('error');
                showScreen(data.message, {}, () => {
                    setTimeout(handleStateChange, 3000, 'MAIN_MENU_IDR');
                });
            }
        }
    }
    async function doPaymentPhone() {
        const paymentData = {
            nomor_hp: tempStorage.nomor_hp,
            amount: tempStorage.amount
        };
        const data = await apiCall('/api/payment/phone', 'POST', paymentData);
        if (data) {
            hideInput();
            tempStorage = {};
            if (data.success) {
                playSound('success');
                showReceipt(data.receipt, 'ASK_CONTINUE');
            } else {
                playSound('error');
                showScreen(data.message, {}, () => {
                    setTimeout(handleStateChange, 3000, 'PAYMENT_MENU');
                });
            }
        }
    }
    async function doPaymentElectricity() {
        const paymentData = {
            nomor_meter: tempStorage.nomor_meter,
            amount: tempStorage.amount
        };
        const data = await apiCall('/api/payment/electricity', 'POST', paymentData);
        if (data) {
            hideInput();
            tempStorage = {};
            if (data.success) {
                playSound('success');
                showReceipt(data.receipt, 'ASK_CONTINUE');
            } else {
                playSound('error');
                showScreen(data.message, {}, () => {
                    setTimeout(handleStateChange, 3000, 'PAYMENT_MENU');
                });
            }
        }
    }
    async function doPaymentWaterCheck(nomor_pelanggan) {
        const data = await apiCall('/api/payment/water_check', 'POST', { nomor_pelanggan: nomor_pelanggan });
        if (data) {
            hideInput();
            if (data.success) {
                playSound('success');
                tempStorage.waterData = data.data;
                const confirmText = [
                    currentTerms['header_konfirmasi_air'],
                    `${currentTerms['tagihan_receipt'].replace('{}', data.data.nama_perusahaan)}`,
                    `${currentTerms['no_pelanggan_receipt'].replace('{}', data.data.nomor_pelanggan_saja)}`,
                    `${currentTerms['nama_receipt'].replace('{}', data.data.nama_pelanggan)}`,
                    `Tagihan           : ${data.data.tagihan_str}`,
                    `${currentTerms['biaya_admin_receipt'].replace('{}', data.data.admin_str)}`,
                    `${currentTerms['total_bayar_receipt'].replace('{}', data.data.total_bayar_str)}`,
                    '------------------------------------------------------------',
                    currentTerms['lanjut_pembayaran_tanya']
                ].join('\n');

                showScreen(confirmText, {
                    r1: { text: currentTerms['opsi_ya'], action: () => doPaymentWaterPay() },
                    r2: { text: currentTerms['opsi_tidak'], action: () => handleStateChange('PAYMENT_MENU') }
                });
            } else {
                showScreen(data.message, {}, () => {
                    setTimeout(handleStateChange, 3000, 'PAYMENT_WATER_INPUT');
                });
            }
        }
    }
    async function doPaymentWaterPay() {
        const data = await apiCall('/api/payment/water_pay', 'POST', tempStorage.waterData);
        if (data) {
            tempStorage = {};
            if (data.success) {
                playSound('success');
                showReceipt(data.receipt, 'ASK_CONTINUE');
            } else {
                showScreen(data.message, {}, () => {
                    setTimeout(handleStateChange, 3000, 'PAYMENT_MENU');
                });
            }
        }
    }
    async function doChangePin() {
        const pinData = {
            pin_lama: tempStorage.pin_lama,
            pin_baru: tempStorage.pin_baru,
            pin_konfirmasi: tempStorage.pin_konfirmasi
        };
        const data = await apiCall('/api/change_pin', 'POST', pinData);
        if (data) {
            hideInput();
            tempStorage = {};
            showScreen(data.message, {}, () => {
                const nextMenu = currentUserData.mata_uang_utama === 'IDR' ? 'MAIN_MENU_IDR' : 'MAIN_MENU_NON_IDR';
                setTimeout(handleStateChange, 3000, nextMenu);
            });
        }
    }
    async function doLogout() {
        await apiCall('/api/logout');
        currentUserData = null;
        tempStorage = {};
        handleStateChange('CARD_EJECTING');
    }

    function handleStateChange(newState) {
        const oldState = appState;
        appState = newState;
        console.log("State changed from", oldState, "to:", newState);

        document.querySelector('.keypad-btn[data-key="."]').disabled = true;

        renderCurrentState();
    }

    function renderCurrentState() {
        switch (appState) {
            case 'INIT':
                showScreen('===== BANK BERKOM A TEBAL =====' + '\n\n' +currentTerms['selamat_datang'] + '\n' + currentTerms['masukkan_kartu_prompt'] + '\n' + currentTerms['tekan_enter_kartu'] + '\n\n//' + '\nWelcome to Bank Berkom A Tebal' + '\nInsert your card to start' + '\nPress Enter to insert card');
                break;

            case 'CARD_INSERTING':
                showLoading(true);
                animateCardIn();
                break;

            case 'WELCOME':
                showLoading(false);
                showScreen(currentTerms['kartu_berhasil'] + '\n' + currentTerms['pilih_bahasa_atm'] + '\n' + '*' + currentTerms['buat_akun'] + '\n\n//' + '\nInsert card successful!' + '\nChoose your preferred language' + '\n*Select \'Buat Akun\' if you don`t have an account', {
                    r1: { text: 'INDONESIA', action: () => setLanguage('id') },
                    r2: { text: 'ENGLISH', action: () => setLanguage('en') },
                    l4: { text: 'BUAT AKUN >', action: () => {
                        window.location.href = '/create_account_page';
                    }}
                });
                break;

            case 'PIN_LOGIN':
                showScreen(currentTerms['masukkan_pin']);
                setupInput('', true);
                break;

            case 'MAIN_MENU_IDR':
                showScreen(currentTerms['pilih_menu_transaksi'], {
                    l1: { text: currentTerms['menu_info_saldo'], action: () => handleStateChange('CHECK_BALANCE') },
                    l2: { text: currentTerms['menu_tarik_tunai'], action: () => handleStateChange('WITHDRAW_IDR_MENU') },
                    l3: { text: currentTerms['menu_transfer'], action: () => handleStateChange('TRANSFER_IDR_START') },
                    r1: { text: currentTerms['menu_pembayaran'], action: () => handleStateChange('PAYMENT_MENU') },
                    r2: { text: currentTerms['menu_ganti_pin'], action: () => handleStateChange('CHANGE_PIN_OLD') },
                    r3: { text: currentTerms['menu_selesai'], action: () => doLogout() }
                });
                break;

            case 'MAIN_MENU_NON_IDR':
                const curr = currentUserData.mata_uang_utama;
                showScreen(currentTerms['menu_utama_non_idr'], {
                    l1: { text: currentTerms['menu_info_saldo_non_idr'].replace('{}', curr), action: () => handleStateChange('CHECK_BALANCE') },
                    l2: { text: currentTerms['menu_tarik_tunai_non_idr'], action: () => handleStateChange('WITHDRAW_NON_IDR_MENU') },
                    r1: { text: currentTerms['menu_ganti_pin_non_idr'], action: () => handleStateChange('CHANGE_PIN_OLD') },
                    r2: { text: currentTerms['menu_selesai_non_idr'], action: () => doLogout() }
                });
                break;

            case 'CHECK_BALANCE':
                doCheckBalance();
                break;

            case 'WITHDRAW_IDR_MENU':
                showScreen(currentTerms['pilih_jumlah_penarikan'], {
                    l1: { text: formatCurrencyJS(50000, 'IDR'), action: () => doWithdrawIDR(50000) },
                    l2: { text: formatCurrencyJS(100000, 'IDR'), action: () => doWithdrawIDR(100000) },
                    r1: { text: formatCurrencyJS(500000, 'IDR'), action: () => doWithdrawIDR(500000) },
                    r2: { text: formatCurrencyJS(1000000, 'IDR'), action: () => doWithdrawIDR(1000000) },
                    r3: { text: currentTerms['jumlah_lain'], action: () => handleStateChange('WITHDRAW_IDR_OTHER') }
                });
                break;
            case 'WITHDRAW_IDR_OTHER':
                showScreen(`${currentTerms['masukkan_jumlah_penarikan_lain']}\n${currentTerms['dalam_kelipatan'].replace('{}', formatCurrencyJS(50000, 'IDR'))}\n${currentTerms['maksimal'].replace('{}', formatCurrencyJS(10000000, 'IDR'))}`);
                setupInput(currentTerms['jumlah_penarikan_input'], false);
                break;

            case 'WITHDRAW_NON_IDR_MENU': {
                const kurs = appConfig.kurs_beli;
                const ccy = currentUserData.mata_uang_utama;
                const ccyData = appConfig.currency_data[ccy]; 
                const stepValue = ccyData.step_curr_lain;
                
                const preset_idr = [50000, 100000, 500000, 1000000];
                
                const preset_curr = preset_idr.map(idr => {
                    const raw = idr / kurs[ccy];
                    return roundToStep(raw, stepValue);
                });

                console.log('[DEBUG] Preset values for', ccy, ':', preset_curr);

                showScreen(`${currentTerms['penarikan_non_idr_header'].replace('{}', ccy)}\n${currentTerms['penarikan_non_idr_prompt']}`, {
                    l1: { 
                        text: `${formatCurrencyJS(preset_idr[0], 'IDR')}\n(${formatCurrencyJS(preset_curr[0], ccy)})`,
                        action: () => {
                            console.log('[DEBUG] Withdrawing:', preset_curr[0], 'type:', typeof preset_curr[0]);
                            doWithdrawNonIDR(preset_curr[0]);
                        }
                    },
                    l2: { 
                        text: `${formatCurrencyJS(preset_idr[1], 'IDR')}\n(${formatCurrencyJS(preset_curr[1], ccy)})`,
                        action: () => {
                            console.log('[DEBUG] Withdrawing:', preset_curr[1], 'type:', typeof preset_curr[1]);
                            doWithdrawNonIDR(preset_curr[1]);
                        }
                    },
                    r1: { 
                        text: `${formatCurrencyJS(preset_idr[2], 'IDR')}\n(${formatCurrencyJS(preset_curr[2], ccy)})`,
                        action: () => {
                            console.log('[DEBUG] Withdrawing:', preset_curr[2], 'type:', typeof preset_curr[2]);
                            doWithdrawNonIDR(preset_curr[2]);
                        }
                    },
                    r2: { 
                        text: `${formatCurrencyJS(preset_idr[3], 'IDR')}\n(${formatCurrencyJS(preset_curr[3], ccy)})`,
                        action: () => {
                            console.log('[DEBUG] Withdrawing:', preset_curr[3], 'type:', typeof preset_curr[3]);
                            doWithdrawNonIDR(preset_curr[3]);
                        }
                    },
                    r3: { 
                        text: currentTerms['penarikan_non_idr_lainnya'].replace('{}', ccy), 
                        action: () => handleStateChange('WITHDRAW_NON_IDR_OTHER') 
                    }
                });
                break;
            }

            case 'WITHDRAW_NON_IDR_OTHER':
                document.querySelector('.keypad-btn[data-key="."]').disabled = false;
                const ccy_data = appConfig.currency_data[currentUserData.mata_uang_utama];
                const ccy_code = currentUserData.mata_uang_utama;
                const text = [
                    currentTerms['masukkan_jumlah_lain_curr'].replace('{}', ccy_code),
                    `(Min: ${formatCurrencyJS(ccy_data.min_amount_curr, ccy_code)})`,
                    `(Max: ${formatCurrencyJS(ccy_data.max_amount_curr_lain, ccy_code)})`,
                    `(Step: ${formatCurrencyJS(ccy_data.step_curr_lain, ccy_code)})`
                ].join('\n');
                showScreen(text);
                setupInput(currentTerms['jumlah_penarikan_curr_input'].replace('{}', ccy_code), false);
                break;

            case 'TRANSFER_IDR_START':
                tempStorage = {};
                showScreen(`${currentTerms['prompt_kode_bank_rek']}\n${currentTerms['ket_kode_bank_rek']}\n${currentTerms['contoh_transfer']}\n\n${currentTerms['lihat_kode_bank_tanya']}`, {
                    r1: { text: currentTerms['opsi_ya'], action: () => handleStateChange('TRANSFER_IDR_SHOW_CODES') },
                    r2: { text: currentTerms['opsi_tidak'], action: () => handleStateChange('TRANSFER_IDR_REK') }
                });
                break;
            case 'TRANSFER_IDR_SHOW_CODES':
                let codesText = currentTerms['daftar_kode_bank'] + '\n\n';
                const banks = appConfig.bank_codes;
                for (const code in banks) {
                    codesText += `${code}: ${banks[code]}\n`;
                }
                showScreen(codesText, {
                    r4: { text: 'LANJUT\n/ CONTINUE', action: () => handleStateChange('TRANSFER_IDR_REK') }
                });
                break;
            case 'TRANSFER_IDR_REK':
                showScreen(currentTerms['prompt_kode_bank_rek']);
                setupInput(currentTerms['rek_tujuan_input'], false);
                break;
            case 'TRANSFER_IDR_AMOUNT':
                hideInput();
                showScreen(currentTerms['nominal_transfer_input']);
                setupInput('Jumlah: ', false);
                break;
            case 'TRANSFER_IDR_CONFIRM':
                const bankName = appConfig.bank_codes[tempStorage.rek_tujuan.substring(0, 3)] || 'BANK TIDAK DIKENAL';
                const confirmText = [
                    currentTerms['konfirmasi_transfer_data'],
                    '---------------------------------------------------',
                    currentTerms['bank_receipt'].replace('{}', bankName),
                    currentTerms['tujuan_receipt'].replace('{}', tempStorage.rek_tujuan),
                    currentTerms['penerima_receipt'].replace('{}', tempStorage.nama_penerima),
                    currentTerms['jumlah_transfer_receipt'].replace('{}', formatCurrencyJS(tempStorage.amount, 'IDR')),
                    '---------------------------------------------------',
                    currentTerms['data_sesuai_tanya']
                ].join('\n');
                showScreen(confirmText, {
                    r1: { text: currentTerms['opsi_ya'], action: () => doTransferIDR() },
                    r2: { text: currentTerms['opsi_tidak'], action: () => handleStateChange('MAIN_MENU_IDR') }
                });
                break;
            case 'PAYMENT_MENU':
                tempStorage = {};
                showScreen(currentTerms['header_pembayaran'], {
                    l1: { text: 'Phone\n/ Mobile', action: () => handleStateChange('PAYMENT_PHONE_INPUT') },
                    l2: { text: 'Electricity\n/ PLN', action: () => handleStateChange('PAYMENT_ELECTRICITY_INPUT') },
                    l3: { text: 'Water\n/ PDAM', action: () => handleStateChange('PAYMENT_WATER_START') },
                    r4: { text: 'KEMBALI / BACK', action: () => handleStateChange('MAIN_MENU_IDR') }
                });
                break;
            case 'PAYMENT_PHONE_INPUT':
                showScreen(currentTerms['prompt_input_telepon']);
                setupInput(currentTerms['nomor_telepon_input'], false);
                break;
            case 'PAYMENT_PHONE_NOMINAL':
                hideInput();
                showScreen(currentTerms['pilih_nominal_pulsa'], {
                    l1: { text: formatCurrencyJS(20000, 'IDR'), action: () => { tempStorage.amount = 20000; handleStateChange('PAYMENT_PHONE_CONFIRM'); }},
                    l2: { text: formatCurrencyJS(30000, 'IDR'), action: () => { tempStorage.amount = 30000; handleStateChange('PAYMENT_PHONE_CONFIRM'); }},
                    l3: { text: formatCurrencyJS(50000, 'IDR'), action: () => { tempStorage.amount = 50000; handleStateChange('PAYMENT_PHONE_CONFIRM'); }},
                    l4: { text: formatCurrencyJS(100000, 'IDR'), action: () => { tempStorage.amount = 100000; handleStateChange('PAYMENT_PHONE_CONFIRM'); }},
                    r1: { text: formatCurrencyJS(150000, 'IDR'), action: () => { tempStorage.amount = 150000; handleStateChange('PAYMENT_PHONE_CONFIRM'); }},
                    r2: { text: formatCurrencyJS(200000, 'IDR'), action: () => { tempStorage.amount = 200000; handleStateChange('PAYMENT_PHONE_CONFIRM'); }},
                    r3: { text: formatCurrencyJS(300000, 'IDR'), action: () => { tempStorage.amount = 300000; handleStateChange('PAYMENT_PHONE_CONFIRM'); }},
                    r4: { text: currentTerms['pulsa_lainnya'], action: () => handleStateChange('PAYMENT_PHONE_OTHER') }
                });
                break;
            case 'PAYMENT_PHONE_OTHER':
                showScreen(currentTerms['masukkan_nominal_lain']);
                setupInput('Jumlah: ', false);
                break;
            case 'PAYMENT_PHONE_CONFIRM':
                const admin_pulsa = 1000;
                const total_pulsa = parseInt(tempStorage.amount) + admin_pulsa;
                const confirmPulsa = [
                    currentTerms['header_konfirmasi_pulsa'],
                    currentTerms['nomor_hp_receipt'].replace('{}', tempStorage.nomor_hp),
                    currentTerms['jumlah_pulsa_receipt'].replace('{}', formatCurrencyJS(tempStorage.amount, 'IDR')),
                    currentTerms['biaya_admin_receipt'].replace('{}', formatCurrencyJS(admin_pulsa, 'IDR')),
                    currentTerms['total_receipt'].replace('{}', formatCurrencyJS(total_pulsa, 'IDR')),
                    '---------------------------------------------------',
                    currentTerms['proses_transaksi_tanya']
                ].join('\n');
                showScreen(confirmPulsa, {
                    r1: { text: currentTerms['opsi_ya'], action: () => doPaymentPhone() },
                    r2: { text: currentTerms['opsi_tidak'], action: () => handleStateChange('PAYMENT_MENU') }
                });
                break;
            case 'PAYMENT_ELECTRICITY_INPUT':
                showScreen(currentTerms['prompt_input_listrik']);
                setupInput(currentTerms['nomor_meter_receipt'].replace('{}', ''), false);
                break;
            case 'PAYMENT_ELECTRICITY_NOMINAL':
                showScreen(`${currentTerms['pilih_nominal_token']}\n${currentTerms['admin_rp_1000']}`, {
                    l1: { text: formatCurrencyJS(20000, 'IDR'), action: () => { tempStorage.amount = 20000; handleStateChange('PAYMENT_ELECTRICITY_CONFIRM'); }},
                    l2: { text: formatCurrencyJS(50000, 'IDR'), action: () => { tempStorage.amount = 50000; handleStateChange('PAYMENT_ELECTRICITY_CONFIRM'); }},
                    l3: { text: formatCurrencyJS(100000, 'IDR'), action: () => { tempStorage.amount = 100000; handleStateChange('PAYMENT_ELECTRICITY_CONFIRM'); }},
                    l4: { text: formatCurrencyJS(200000, 'IDR'), action: () => { tempStorage.amount = 200000; handleStateChange('PAYMENT_ELECTRICITY_CONFIRM'); }},
                    r1: { text: formatCurrencyJS(500000, 'IDR'), action: () => { tempStorage.amount = 500000; handleStateChange('PAYMENT_ELECTRICITY_CONFIRM'); }},
                    r2: { text: formatCurrencyJS(1000000, 'IDR'), action: () => { tempStorage.amount = 1000000; handleStateChange('PAYMENT_ELECTRICITY_CONFIRM'); }},
                    r3: { text: formatCurrencyJS(5000000, 'IDR'), action: () => { tempStorage.amount = 5000000; handleStateChange('PAYMENT_ELECTRICITY_CONFIRM'); }},
                    r4: { text: formatCurrencyJS(10000000, 'IDR'), action: () => { tempStorage.amount = 10000000; handleStateChange('PAYMENT_ELECTRICITY_CONFIRM'); }}
                });
                break;
            case 'PAYMENT_ELECTRICITY_CONFIRM':
                const admin_listrik = 1000;
                const total_listrik = parseInt(tempStorage.amount) + admin_listrik;
                const confirmListrik = [
                    currentTerms['header_konfirmasi_listrik'],
                    currentTerms['nomor_meter_receipt'].replace('{}', tempStorage.nomor_meter),
                    currentTerms['nama_receipt'].replace('{}', currentUserData.nama_lengkap),
                    currentTerms['tarif_daya_receipt'],
                    currentTerms['jumlah_pulsa_receipt'].replace('{}', formatCurrencyJS(tempStorage.amount, 'IDR')),
                    currentTerms['biaya_admin_receipt'].replace('{}', formatCurrencyJS(admin_listrik, 'IDR')),
                    currentTerms['total_receipt'].replace('{}', formatCurrencyJS(total_listrik, 'IDR')),
                    '---------------------------------------------------',
                    currentTerms['proses_transaksi_tanya']
                ].join('\n');
                showScreen(confirmListrik, {
                    r1: { text: currentTerms['opsi_ya'], action: () => doPaymentElectricity() },
                    r2: { text: currentTerms['opsi_tidak'], action: () => handleStateChange('PAYMENT_MENU') }
                });
                break;
            case 'PAYMENT_WATER_START':
                showScreen(`${currentTerms['prompt_input_air']}\n${currentTerms['contoh_air']}\n\n${currentTerms['lihat_kode_pdam_tanya']}`, {
                    r1: { text: currentTerms['opsi_ya'], action: () => handleStateChange('PAYMENT_WATER_SHOW_CODES') },
                    r2: { text: currentTerms['opsi_tidak'], action: () => handleStateChange('PAYMENT_WATER_INPUT') }
                });
                break;
            case 'PAYMENT_WATER_SHOW_CODES':
                let pdamCodesText = currentTerms['daftar_kode_pdam'] + '\n\n';
                const pdam_codes = appConfig.pdam_codes;
                for (const code in pdam_codes) {
                    pdamCodesText += `${code}: ${pdam_codes[code]}\n`;
                }
                showScreen(pdamCodesText, {
                    r4: { text: 'LANJUT\n/ CONTINUE', action: () => handleStateChange('PAYMENT_WATER_INPUT') }
                });
                break;
            case 'PAYMENT_WATER_INPUT':
                showScreen(currentTerms['prompt_input_air']);
                setupInput(currentTerms['nomor_pelanggan_input'], false);
                break;
            case 'CHANGE_PIN_OLD':
                tempStorage = {};
                showScreen(currentTerms['masukkan_pin_lama']);
                setupInput('', true);
                break;
            case 'CHANGE_PIN_NEW':
                showScreen(currentTerms['masukkan_pin_baru']);
                setupInput('', true);
                break;
            case 'CHANGE_PIN_CONFIRM':
                showScreen(currentTerms['konfirmasi_pin_baru']);
                setupInput('', true);
                break;
            case 'ASK_CONTINUE':
                const nextMenuState = currentUserData.mata_uang_utama === 'IDR' ? 'MAIN_MENU_IDR' : 'MAIN_MENU_NON_IDR';
                showScreen(currentTerms['perlu_transaksi_lain'], {
                    r1: { text: currentTerms['opsi_ya'], action: () => handleStateChange(nextMenuState) },
                    r2: { text: currentTerms['opsi_tidak'], action: () => doLogout() }
                });
                break;
            case 'CARD_EJECTING':
                showScreen(currentTerms['ambil_kartu'] + '\n\n' + currentTerms['terima_kasih']);
                animateCardOut();
                break;
        }
    }

    function showDenominationChoice(amount) {
        currentWithdrawalAmount = amount;
        const amountStr = formatCurrencyJS(amount, 'IDR');

        const choiceText = `PILIH PECAHAN / SELECT DENOMINATIONS: \nRp50.000 or Rp100.000`
        
        const btn50Text = 'Rp50.000\n';
        const btn100Text = 'Rp100.000\n';

        const successMessage = currentTerms['penarikan_berhasil'].replace('{}', amountStr);
        
        showScreen(
            successMessage + '\n\n' + choiceText,
            {
                l1: { 
                    text: btn50Text, 
                    action: () => dispenseCash('50k', amount) 
                },
                l2: { 
                    text: btn100Text, 
                    action: () => dispenseCash('100k', amount) 
                }
            }
        );
    }

    function dispenseCash(denomination, totalAmount) {
        sideButtons.forEach(btn => {
            btn.style.visibility = 'hidden';
        });

        const noteValue = denomination === '50k' ? 50000 : 100000;
        const noteCount = Math.floor(totalAmount / noteValue);
        const valueStr = formatCurrencyJS(noteValue, 'IDR');

        showScreen(
            `${currentTerms['harap_menunggu']}\n\n` +
            `Sedang mengeluarkan ${noteCount} lembar /\nDispensing notes of ${noteCount} sheets \n` +
            `${valueStr}...`
        );

        const cashNotesContainer = document.getElementById('cash-notes-container');

        setTimeout(() => {
            playSound('cashDispense');
            for (let i = 0; i < noteCount; i++) {
                setTimeout(() => {
                    const cashNote = document.createElement('div');
                    cashNote.className = `cash-note ${denomination === '50k' ? 'blue-50k' : 'red-100k'}`;
                    cashNote.setAttribute('data-value', valueStr);
                    cashNote.style.bottom = `${-80 - (i * 5)}px`;
                    cashNote.style.zIndex = noteCount - i;
                    cashNotesContainer.appendChild(cashNote);

                    setTimeout(() => {
                        cashNote.classList.add('dispensing');
                    }, 50);
                }, i * 400);
            }

            setTimeout(() => {
                const ccyCode = currentUserData.mata_uang_utama;
                const saldoTerkini = formatCurrencyJS(currentUserData.saldo, ccyCode);
                showScreen(
                    `${currentTerms['transaksi_berhasil']}\n\n` +
                    `Silakan ambil uang Anda / Please take your money\n` +
                    `Total: ${formatCurrencyJS(totalAmount, 'IDR')}\n` +
                    `Pecahan/Denominations: ${noteCount} lembar (sheets) ${valueStr}\n\n` +
                    `${currentTerms['sisa_saldo_anda'].replace('{}', saldoTerkini)}\n\n` +
                    `${currentTerms['cetak_receipt_tanya']}`,
                    {
                        r1: { 
                            text: currentTerms['opsi_ya'], 
                            action: () => {
                                collectCash();
                                generateAndShowReceipt(totalAmount, denomination);
                            }
                        },
                        r2: { 
                            text: currentTerms['opsi_tidak'], 
                            action: () => {
                                collectCash();
                                handleStateChange('ASK_CONTINUE');
                            }
                        }
                    }
                );
            }, noteCount * 400 + 1500);
        }, 1000);
    }

    function collectCash() {
        const cashNotes = document.querySelectorAll('.cash-note');
        cashNotes.forEach((note, index) => {
            setTimeout(() => {
                note.classList.add('collected');
                setTimeout(() => {
                    note.remove();
                }, 800);
            }, index * 100);
        });
    }

    function generateAndShowReceipt(amount, denomination) {
        const waktu = new Date().toISOString().split('T').join(' ').split('.')[0];
        const noteValue = denomination === '50k' ? 50000 : 100000;
        const noteCount = Math.floor(amount / noteValue);
        const valueStr = formatCurrencyJS(noteValue, 'IDR');
        const ccyCode = currentUserData.mata_uang_utama;
        const saldoTerkini = formatCurrencyJS(currentUserData.saldo, ccyCode);
        
        const struk = [
            '---------------------------------------------------',
            currentTerms['header_receipt_tarik'],
            currentTerms['jumlah_receipt'].replace('{}', formatCurrencyJS(amount, 'IDR')),
            `Pecahan/Denominations: ${noteCount} lembar (sheets) ${valueStr}`,
            currentTerms['sisa_saldo_receipt'].replace('{}', saldoTerkini),
            currentTerms['waktu_transaksi_receipt'].replace('{}', waktu),
            '---------------------------------------------------'
        ].join('\n');

        showReceipt(struk, 'ASK_CONTINUE');
    }

    initializeApp();

});