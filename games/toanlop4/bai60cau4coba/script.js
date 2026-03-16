document.addEventListener('DOMContentLoaded', () => {
    const btnCheck = document.getElementById('check-btn');
    const inputNum = document.getElementById('ans-num');
    const inputDen = document.getElementById('ans-den');
    const feedbackArea = document.getElementById('feedback-area');
    const feedbackText = document.getElementById('feedback-text');
    const feedbackIcon = document.getElementById('feedback-icon');

    btnCheck.addEventListener('click', checkAnswer);

    function checkAnswer() {
        const numVal = inputNum.value.trim();
        const denVal = inputDen.value.trim();
        
        feedbackArea.classList.remove('feedback-hidden');
        
        if (numVal === '' || denVal === '') {
            showError('🤔', 'Con hãy điền đầy đủ tử số và mẫu số nhé!');
            return;
        }

        const num = parseInt(numVal, 10);
        const den = parseInt(denVal, 10);

        // Đáp án đúng là 13/15
        if (num === 13 && den === 15) {
            showSuccess('🎉', 'Giỏi quá! Con đã tính đúng rồi. Cô Ba đã dùng tất cả 13/15 tấm vải.');
            triggerConfetti();
        } else {
            // Phân tích lỗi sai để gợi ý
            if (den !== 15 && num === 13) {
                showError('💡', 'Chú ý nhé: Khi cộng các phân số có CÙNG mẫu số, ta cộng các tử số và GIỮ NGUYÊN mẫu số. Mẫu số vẫn phải là số mấy nhỉ?');
            } else if (den === 45) { // Lỗi cộng luôn mẫu số
                showError('🧐', 'Trời ơi, con lại lấy 15 + 15 + 15 à? Nhớ là phân số cùng mẫu thì mình chỉ cộng tử số và giữ nguyên mẫu số nhé!');
            } else if (den === 15 && num !== 13) {
                // Tính sai tổng tử số
                showError('✍️', 'Con thử nhẩm lại tổng của tử số xem nào: 7 + 4 + 2 bằng bao nhiêu nhỉ? Cố lên!');
            } else {
                // Sai chung
                showError('🔍', 'Chưa đúng rồi. Con hãy nhớ: Muốn tìm tổng số phần vải cô Ba đã dùng, ta làm phép cộng 3 phân số: 7/15 + 4/15 + 2/15 nha.');
            }
        }
    }

    function showSuccess(icon, text) {
        feedbackIcon.textContent = icon;
        feedbackText.textContent = text;
        feedbackArea.classList.remove('feedback-error');
        feedbackArea.classList.add('feedback-success');
    }

    function showError(icon, text) {
        feedbackIcon.textContent = icon;
        feedbackText.textContent = text;
        feedbackArea.classList.remove('feedback-success');
        feedbackArea.classList.add('feedback-error');
    }

    function triggerConfetti() {
        var duration = 3 * 1000;
        var animationEnd = Date.now() + duration;
        var defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

        function randomInRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        var interval = setInterval(function() {
            var timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) {
                return clearInterval(interval);
            }

            var particleCount = 50 * (timeLeft / duration);
            confetti(Object.assign({}, defaults, { particleCount,
                origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
            }));
            confetti(Object.assign({}, defaults, { particleCount,
                origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
            }));
        }, 250);
    }
});
