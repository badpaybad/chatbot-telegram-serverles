const gameData = {
    a1: {
        num: 5, den: 21, id: 'wrap-a1',
        hints: [
            "💡 Để làm phép tính cộng này, em hãy nhớ quy đồng mẫu số của 2 phân số nhé.",
            "🔍 Phần a) mẫu chung là 21. Em hãy quy đồng phân số thứ hai (1/7) bằng cách nhân cả tử và mẫu với 3.",
            "✍️ Ta có: 1/7 = 3/21. Bây giờ em tính: 2/21 + 3/21 và nhập kết quả nhé!"
        ],
        hintLevel: 0
    },
    a2: {
        num: 26, den: 21, id: 'wrap-a2',
        hints: [
            "💡 Khi cộng một phân số với 1, em hãy biến số 1 thành phân số có cùng mẫu số nhé.",
            "🔍 Em hãy viết 1 dưới dạng phân số có mẫu số là 21 nhé. (Đó là 21/21 đấy!)",
            "✍️ Ta tính xem kết quả của phép cộng này là bao nhiêu: 5/21 + 21/21."
        ],
        hintLevel: 0
    },
    b1: {
        num: 14, den: 25, id: 'wrap-b1',
        hints: [
            "💡 Tương tự, em cần quy đồng mẫu số của 2 phân số này (mẫu số chung là 25).",
            "🔍 Em thử quy đồng phân số 1/5 bằng cách nhân cả tử và mẫu với 5 xem sao nhé.",
            "✍️ Phân số thứ hai là: 1/5 = 5/25. Giờ em làm phép cộng: 9/25 + 5/25 sẽ ra bao nhiêu?"
        ],
        hintLevel: 0
    },
    b2: {
        num: 9, den: 25, id: 'wrap-b2',
        hints: [
            "💡 Ở đây là phép trừ phân số! Nhớ quy đồng mẫu số giống như ở phép cộng nhé.",
            "🔍 Ta đã biết 1/5 = 5/25 từ bước trước. Em hãy thay vào để làm phép trừ.",
            "✍️ Ta lấy 14/25 trừ đi 5/25 (14/25 - 5/25). Em nhập kết quả mới nhất nhé!"
        ],
        hintLevel: 0
    }
};

// Đổi chuỗi text dạng "2/21" thành dạng hiển thị phân số trên web
function renderFrac(n, d) {
    return `<span style="display:inline-flex;flex-direction:column;vertical-align:middle;text-align:center;font-size:1.1em;line-height:1.2;margin:0 4px;"><span style="border-bottom:2px solid #533f03;padding:0 3px;">${n}</span><span>${d}</span></span>`;
}

function formatHint(text) {
    return text.replace(/(\d+)\/(\d+)/g, (match, n, d) => renderFrac(n, d));
}

let firstErrorKey = null;

function checkAnswers() {
    let allCorrect = true;
    firstErrorKey = null;

    // Xóa class error cũ (nếu có)
    for(let key in gameData) {
        document.getElementById(gameData[key].id).classList.remove('error');
    }

    const keys = ['a1', 'a2', 'b1', 'b2'];
    
    for (const key of keys) {
        const item = gameData[key];
        const numInput = document.getElementById(`${key}-num`);
        const denInput = document.getElementById(`${key}-den`);
        
        // Chỉ kiểm tra các ô tính chưa bị vô hiệu hóa (tức là chưa làm đúng)
        if (!numInput.disabled) {
            const nVal = parseInt(numInput.value);
            const dVal = parseInt(denInput.value);
            
            // Nếu đúng kết quả số
            if (nVal === item.num && dVal === item.den) {
                const wrap = document.getElementById(item.id);
                wrap.classList.add('correct');
                numInput.disabled = true;
                denInput.disabled = true;
                item.hintLevel = 0; // Đặt lại gợi ý
            } else {
                allCorrect = false;
                
                // Ghi lại lỗi đầu tiên gặp phải để hiện gợi ý
                if (!firstErrorKey) {
                    firstErrorKey = key;
                }
            }
        }
    }

    const feedbackBox = document.getElementById('feedback-box');
    const feedbackText = document.getElementById('feedback-text');

    if (allCorrect) {
        feedbackBox.classList.remove('active');
        showSuccessModal();
    } else {
        if (firstErrorKey) {
            const wrap = document.getElementById(gameData[firstErrorKey].id);
            
            // Xóa animation rồi thêm lại để hiệu ứng rung hoạt động nhiều lần
            wrap.classList.remove('error');
            void wrap.offsetWidth; // trigger DOM reflow
            wrap.classList.add('error');
            
            const item = gameData[firstErrorKey];
            const hint = item.hints[Math.min(item.hintLevel, item.hints.length - 1)];
            
            // Tăng level gợi ý cho lần kiểm tra sai tiếp theo
            if (item.hintLevel < item.hints.length - 1) {
                item.hintLevel++;
            }
            
            feedbackText.innerHTML = formatHint(hint);
            feedbackBox.classList.add('active');
        }
    }
}

function showSuccessModal() {
    confetti({
        particleCount: 150,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#4a69bd', '#78e08f', '#fbd38d', '#f6b93b', '#e55039']
    });
    document.getElementById('success-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('success-modal').classList.remove('active');
}

// Lắng nghe sự kiện click trên nút "Kiểm tra kết quả"
document.getElementById('btn-check').addEventListener('click', checkAnswers);

// Lắng nghe phím Enter trong các ô input
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            checkAnswers();
        }
    });
});
