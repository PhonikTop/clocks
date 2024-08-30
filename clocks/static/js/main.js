document.addEventListener('DOMContentLoaded', function() {
    const socket = new WebSocket(`ws://127.0.0.1:8000/ws/room/12`);

    socket.onopen = function(e) {
        console.log('WebSocket connection established');
    };

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log('Received data:', data);

        // Обработка данных о участниках
        if (data.participants) {
            console.log('Participants data:', data.participants);
            updateParticipants(data.participants);
        } else {
            console.warn('No participants data received');
        }

        // Обработка данных о голосах
        if (data.votes) {
            console.log('Votes data:', data.votes);
            updateVotes(data.votes);
        } else {
            console.warn('No votes data received');
        }
    };

    socket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };

    socket.onclose = function(e) {
        console.error('WebSocket connection closed unexpectedly');
    };

    // Обработка нажатия кнопки для обновления участников
    const refreshButton = document.getElementById('refresh-participants-btn');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            console.log('Refresh button clicked');
            socket.send(JSON.stringify({ action: 'refresh_participants' }));
        });
    } else {
        console.error('Refresh button not found');
    }

    // Обработка отправки формы
    const voteForm = document.getElementById('vote-form');
    if (voteForm) {
        voteForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Предотвратить отправку формы по умолчанию

            const userId = document.getElementById('user-id').value;
            const voteValue = document.getElementById('vote-value').value;

            console.log('Submitting vote:', { userId, voteValue });

            socket.send(JSON.stringify({
                action: 'submit_vote',
                user_id: userId,
                vote: voteValue
            }));
        });
    } else {
        console.error('Vote form not found');
    }

    function updateParticipants(participants) {
        const participantsList = document.getElementById('participants-list');
        participantsList.innerHTML = ''; // Очистить старые данные

        if (!Array.isArray(participants)) {
            console.error('Invalid participants data:', participants);
            return;
        }

        participants.forEach(participant => {
            const li = document.createElement('li');
            li.textContent = `${participant.username} (${participant.role}): ${participant.status}`;
            participantsList.appendChild(li);
        });
    }

    function updateVotes(votes) {
        const votesList = document.getElementById('votes-list');
        votesList.innerHTML = ''; // Очистить старые данные

        if (!votes || typeof votes !== 'object') {
            console.error('Invalid votes data:', votes);
            return;
        }

        for (const [meetingId, voteList] of Object.entries(votes)) {
            const meetingDiv = document.createElement('div');
            meetingDiv.innerHTML = `<h3>Meeting ${meetingId}</h3>`;

            if (!Array.isArray(voteList)) {
                console.error('Invalid vote list for meeting:', meetingId, voteList);
                continue;
            }

            voteList.forEach(vote => {
                const p = document.createElement('p');
                p.textContent = `${vote.user__username}: ${vote.vote}`;
                meetingDiv.appendChild(p);
            });

            votesList.appendChild(meetingDiv);
        }
    }
});
