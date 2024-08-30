document.addEventListener('DOMContentLoaded', () => {
    const socket = new WebSocket('ws://127.0.0.1:8000/ws/room/12');

    socket.addEventListener('open', () => {
        console.log('WebSocket connection established');
    });

    socket.addEventListener('message', (e) => {
        const data = JSON.parse(e.data);
        console.log('Received data:', data);

        if (data.participants) {
            updateParticipants(data.participants);
        } else {
            console.warn('No participants data received');
        }

        if (data.votes) {
            updateVotes(data.votes);
        } else {
            console.warn('No votes data received');
        }
    });

    socket.addEventListener('error', (e) => {
        console.error('WebSocket error:', e);
    });

    socket.addEventListener('close', () => {
        console.error('WebSocket connection closed unexpectedly');
    });

    const refreshButton = document.getElementById('refresh-participants-btn');
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            console.log('Refresh button clicked');
            socket.send(JSON.stringify({ action: 'refresh_participants' }));
        });
    } else {
        console.error('Refresh button not found');
    }

    const voteForm = document.getElementById('vote-form');
    if (voteForm) {
        voteForm.addEventListener('submit', (event) => {
            event.preventDefault();

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
        participantsList.innerHTML = '';

        if (!Array.isArray(participants)) {
            console.error('Invalid participants data:', participants);
            return;
        }

        participants.forEach(({ username, role, status }) => {
            const li = document.createElement('li');
            li.textContent = `${username} (${role}): ${status}`;
            participantsList.appendChild(li);
        });
    }

    function updateVotes(votes) {
        const votesList = document.getElementById('votes-list');
        votesList.innerHTML = ''; // Очистить старые данные

        if (typeof votes !== 'object' || votes === null) {
            console.error('Invalid votes data:', votes);
            return;
        }

        for (const [username, vote] of Object.entries(votes)) {
            const p = document.createElement('p');
            p.textContent = `${username}: ${vote}`;
            votesList.appendChild(p);
        }
    }
});
