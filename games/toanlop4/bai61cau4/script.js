document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.draggable-card');
    const dropZones = document.querySelectorAll('.drop-zone');
    const hintBox = document.getElementById('hint-box');
    const hintText = document.getElementById('hint-text');
    const planetImg = document.getElementById('planet-img');
    
    let draggedCard = null;
    let correctCount = 0;
    let errorCount = {};
    const totalSlots = 6;

    // Help messages based on the letter to guide students (scaffolding)
    const hints = {
        'A': {
            start: 'Thử quy đồng mẫu số nhé. Mẫu số chung của 18 và 6 là bao nhiêu?',
            errors: [
                'Em thử nhân cả tử và mẫu của 1/6 với 3 xem sao.',
                '1/6 sẽ bằng 3/18 đấy. Giờ em thử lấy 5/18 trừ 3/18 xem kết quả là bao nhiêu?',
                'Kết quả là 2/18, nhưng em đừng quên rút gọn về phân số tối giản nhé (chia cả tử và mẫu cho 2)!'
            ]
        },
        'H': {
            start: 'Phép trừ có khác mẫu số. Hãy tìm mẫu số chung của 6 và 18 nhé.',
            errors: [
                'Mẫu số chung là 18. Em hãy quy đồng phân số 3/6 nhé.',
                '3/6 bằng 9/18 đúng không nào? Giờ em lấy 9/18 trừ 1/18 xem sao.',
                'Kết quả bằng 8/18. Em hãy rút gọn phân số này bằng cách chia cả tử và mẫu cho 2 nhé!'
            ]
        },
        'S': {
             start: 'Chữ S: Phép cộng phân số. Hãy quy đồng mẫu số về 18 nhé.',
             errors: [
                 'Em hãy quy đồng phân số 2/9. Cả tử và mẫu nhân với 2 nha.',
                 '2/9 = 4/18. Giờ thì em thực hiện phép cộng 4/18 + 1/18 nào.',
                 'Đúng rồi, tử số 4 + 1 = 5. Vậy đáp án là 5/18 nhé!'
             ]
        },
        'O': {
             start: 'Chữ O: Có ba phân số cùng mẫu số là 18. Rất dễ phải không?',
             errors: [
                 'Vì cùng mẫu số nên em chỉ cần giữ nguyên mẫu số và trừ các tử số cho nhau thôi.',
                 'Hãy lấy tử số: 7 - 5 - 1 = ? rồi phần 18.',
                 'Chính xác! 7 trừ 5 trừ 1 bằng 1. Đáp án là 1/18 nhé!'
             ]
        },
        'Ổ': {
             start: 'Chữ Ổ: Cả ba phân số đều có chung mẫu số là 22 nè.',
             errors: [
                 'Tương tự, em giữ nguyên mẫu số 22 và thực hiện các phép tính với tử số.',
                 'Hãy tính: 5 + 7 - 3 = ?',
                 '5 cộng 7 bằng 12, trừ đi 3 còn 9. Vậy phân số cần tìm là 9/22!'
             ]
        },
        'T': {
             start: 'Chữ T: Cũng là các phân số có mẫu số bằng 22. Cùng làm phép tính nào!',
             errors: [
                 'Em hãy lấy các tử số 2 + 7 - 1 xem bằng mấy?',
                 'Kết quả tử số là 8. Em được phân số 8/22. Hãy nhớ rút gọn nó nhé.',
                 'Để rút gọn 8/22, em thử chia cả tử số và mẫu số cho 2 xem!'
             ]
        }
    };

    // Initialize display hint 
    setTimeout(() => {
        hintBox.classList.remove('hidden');
    }, 1000);

    const showHint = (msg, isSuccess = false) => {
        hintText.innerText = msg;
        if(isSuccess) {
            hintBox.classList.add('success');
        } else {
            hintBox.classList.remove('success');
        }
        
        // bounce animation for robot
        const character = document.querySelector('#character img');
        character.style.animation = 'none';
        void character.offsetWidth; // trigger reflow
        character.style.animation = 'bounce 0.5s ease-in-out 2';
    };

    cards.forEach(card => {
        card.addEventListener('dragstart', (e) => {
            draggedCard = card;
            e.dataTransfer.setData('text/plain', card.dataset.letter);
            setTimeout(() => card.classList.add('dragging'), 0);
            
            // Show hint when they start dragging
            showHint(hints[card.dataset.letter].start);
        });

        card.addEventListener('dragend', () => {
            draggedCard.classList.remove('dragging');
        });
        
        // Fallback for touch devices (click to select and click to place)
        card.addEventListener('click', () => {
             if(draggedCard && draggedCard !== card) {
                 draggedCard.style.border = '';
             }
             draggedCard = card;
             card.style.border = '2px solid #ff4757';
             showHint(hints[card.dataset.letter].start);
        });
    });

    dropZones.forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('hovered');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('hovered');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('hovered');
            
            const letter = e.dataTransfer.getData('text/plain');
            handleDropOrClick(zone, letter);
        });
        
        zone.addEventListener('click', () => {
            if(draggedCard) {
                const letter = draggedCard.dataset.letter;
                handleDropOrClick(zone, letter);
                draggedCard.style.border = '';
                draggedCard = null;
            }
        });
    });
    
    function handleDropOrClick(zone, letter) {
        if(zone.classList.contains('filled')) return; // already filled
        
        const expectedLetter = zone.parentElement.dataset.expected;
        
        if(letter === expectedLetter) {
            // Correct match
            zone.innerText = letter;
            zone.classList.add('filled');
            
            // hide the card
            document.querySelector(`.draggable-card[data-letter="${letter}"]`).style.display = 'none';
            
            correctCount++;
            
            if(correctCount === totalSlots) {
                showWinSequence();
            } else {
                showHint('Chính xác! Giỏi quá!', true);
            }
            
        } else {
            // Incorrect match
            zone.classList.add('shake');
            setTimeout(() => zone.classList.remove('shake'), 500);
            
            errorCount[letter] = (errorCount[letter] || 0);
            const errorHints = hints[letter].errors;
            const hintIndex = Math.min(errorCount[letter], errorHints.length - 1);
            showHint('Chưa chính xác rồi! ' + errorHints[hintIndex]);
            errorCount[letter]++;
        }
    }

    function showWinSequence() {
        showHint('Chúc mừng con! Ô chữ là SAO THỔ. Trái đất của chúng ta cũng là một hành tinh đó!', true);
        planetImg.style.display = 'inline-block';
        
        // Fire confetti
        const end = Date.now() + 3 * 1000;
        const colors = ['#ff4757', '#2ed573', '#ffa502', '#5352ed'];

        (function frame() {
            confetti({
                particleCount: 5,
                angle: 60,
                spread: 55,
                origin: { x: 0 },
                colors: colors
            });
            confetti({
                particleCount: 5,
                angle: 120,
                spread: 55,
                origin: { x: 1 },
                colors: colors
            });

            if (Date.now() < end) {
                requestAnimationFrame(frame);
            }
        }());
    }
});
