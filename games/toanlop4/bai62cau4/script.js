document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const numInput = document.getElementById('ans-numerator');
    const denInput = document.getElementById('ans-denominator');
    const checkBtn = document.getElementById('check-btn');
    const feedbackMsg = document.getElementById('feedback-message');
    const messageText = document.getElementById('message-text');
    const successModal = document.getElementById('success-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');

    // State
    let attemptCount = 0;
    const CORRECT_NUMERATOR = 13;
    const CORRECT_DENOMINATOR = 8;

    // Hints
    const hints = [
        "Để tính khúc gỗ thứ ba, em cần lấy chiều dài cả cây gỗ trừ đi chiều dài của hai khúc đã biết nhé!",
        "Phép tính của chúng ta là: <span class='fraction-inline'><span class='numerator'>17</span><span class='denominator'>4</span></span> - <span class='fraction-inline'><span class='numerator'>3</span><span class='denominator'>2</span></span> - <span class='fraction-inline'><span class='numerator'>9</span><span class='denominator'>8</span></span>. Em hãy thử quy đồng với mẫu số chung là 8 nào!",
        "Gợi ý cuối: Ta có <span class='fraction-inline'><span class='numerator'>17</span><span class='denominator'>4</span></span> = <span class='fraction-inline'><span class='numerator'>34</span><span class='denominator'>8</span></span>, và <span class='fraction-inline'><span class='numerator'>3</span><span class='denominator'>2</span></span> = <span class='fraction-inline'><span class='numerator'>12</span><span class='denominator'>8</span></span>. Vậy <span class='fraction-inline'><span class='numerator'>34</span><span class='denominator'>8</span></span> - <span class='fraction-inline'><span class='numerator'>12</span><span class='denominator'>8</span></span> - <span class='fraction-inline'><span class='numerator'>9</span><span class='denominator'>8</span></span> bằng phân số nào nhỉ?"
    ];

    // Functions
    function showMessage(msg, isError) {
        messageText.innerHTML = msg;
        feedbackMsg.className = `message-box ${isError ? 'error' : 'hint'}`;
        feedbackMsg.classList.remove('hidden');
    }

    function hideMessage() {
        feedbackMsg.classList.add('hidden');
    }

    function triggerConfetti() {
        var duration = 3 * 1000;
        var animationEnd = Date.now() + duration;
        var defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 200 };

        function randomInRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        var interval = setInterval(function() {
            var timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) {
                return clearInterval(interval);
            }

            var particleCount = 50 * (timeLeft / duration);
            confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } }));
            confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } }));
        }, 250);
    }

    function handleCheck() {
        hideMessage();
        
        const numVal = numInput.value.trim();
        const denVal = denInput.value.trim();

        if (!numVal || !denVal) {
            showMessage("Em nhớ điền đủ cả tử số và mẫu số nhé!", true);
            return;
        }

        const n = parseInt(numVal);
        const d = parseInt(denVal);

        if (isNaN(n) || isNaN(d)) {
            showMessage("Vui lòng nhập số hợp lệ!", true);
            return;
        }

        if (d === 0) {
            showMessage("Mẫu số không thể bằng 0 em nhé!", true);
            return;
        }

        // Check Correctness
        // Chấp nhận các phân số tương đương, nhưng khuyến khích rút gọn
        // Ở đây đáp án 13/8 là tối giản rồi
        if (n * CORRECT_DENOMINATOR === d * CORRECT_NUMERATOR) {
            if (n === CORRECT_NUMERATOR && d === CORRECT_DENOMINATOR) {
                // Hoàn toàn chính xác
                numInput.style.borderColor = '#4CAF50';
                denInput.style.borderColor = '#4CAF50';
                numInput.style.backgroundColor = '#e8f5e9';
                denInput.style.backgroundColor = '#e8f5e9';
                
                triggerConfetti();
                setTimeout(() => {
                    successModal.classList.remove('hidden');
                }, 1000);
            } else {
                showMessage(`Đúng rồi! Nhưng em thử rút gọn phân số <span class='fraction-inline'><span class='numerator'>${n}</span><span class='denominator'>${d}</span></span> xem sao.`, false);
            }
        } else {
            // Incorrect
            attemptCount++;
            let hintIndex = Math.min(attemptCount - 1, hints.length - 1);
            showMessage(`Chưa chính xác rùi! 😔<br><br>${hints[hintIndex]}`, true);
            
            // Lắc nhẹ input
            numInput.classList.add('shake');
            denInput.classList.add('shake');
            setTimeout(() => {
                numInput.classList.remove('shake');
                denInput.classList.remove('shake');
            }, 500);
        }
    }

    // Event Listeners
    checkBtn.addEventListener('click', handleCheck);

    numInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') denInput.focus();
    });

    denInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleCheck();
    });

    closeModalBtn.addEventListener('click', () => {
        successModal.classList.add('hidden');
    });

});

// Thêm CSS class cho hiệu ứng rung (shake)
const style = document.createElement('style');
style.innerHTML = `
.shake {
    animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}
@keyframes shake {
    10%, 90% { transform: translate3d(-1px, 0, 0); }
    20%, 80% { transform: translate3d(2px, 0, 0); }
    30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
    40%, 60% { transform: translate3d(4px, 0, 0); }
}
`;
document.head.appendChild(style);
