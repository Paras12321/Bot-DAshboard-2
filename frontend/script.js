const API = '/api';

let botsCache = [];

// ===== TOAST =====

function showToast(message, type = 'info') {

    const c = document.getElementById('toastContainer');

    if (!c) return;

    const t = document.createElement('div');

    t.className = `toast ${type}`;

    t.innerHTML = `
        <span class="toast-message">${message}</span>
    `;

    c.appendChild(t);

    setTimeout(() => {
        t.remove();
    }, 4000);
}

// ===== API HELPERS =====

async function apiGet(endpoint) {

    try {

        const response = await fetch(API + endpoint);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.json();

    } catch (e) {

        console.error(e);

        showToast('Failed to fetch data', 'error');

        return null;
    }
}

async function apiPost(endpoint, data) {

    try {

        const response = await fetch(API + endpoint, {

            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify(data)
        });

        const json = await response.json();

        if (!response.ok) {
            throw new Error(json.detail || `HTTP ${response.status}`);
        }

        return json;

    } catch (e) {

        console.error(e);

        showToast(e.message, 'error');

        return null;
    }
}

async function apiDelete(endpoint) {

    try {

        const response = await fetch(API + endpoint, {
            method: 'DELETE'
        });

        return response.ok || response.status === 204;

    } catch {

        showToast('Delete failed', 'error');

        return false;
    }
}

// ===== UTILS =====

function val(id) {

    const el = document.getElementById(id);

    return el ? el.value.trim() : '';
}

function setText(id, value) {

    const el = document.getElementById(id);

    if (el) {
        el.textContent = value;
    }
}

function esc(text) {

    if (!text) return '';

    const div = document.createElement('div');

    div.textContent = text;

    return div.innerHTML;
}

function fmtDate(date) {

    if (!date) return '-';

    return new Date(date).toLocaleString();
}

function capitalize(text) {

    return text
        ? text.charAt(0).toUpperCase() + text.slice(1)
        : '';
}

function toggleTokenVis() {

    const input = document.getElementById('botToken');

    input.type =
        input.type === 'password'
            ? 'text'
            : 'password';
}

// ===== LOAD BOTS =====

async function loadBots() {

    const bots = await apiGet('/bots/');

    if (!bots) return;

    botsCache = bots;

    populateBotSelects();

    updateStats();
}

function populateBotSelects() {

    const activeBots =
        botsCache.filter(bot => bot.is_active);

    ['msgBot', 'arBot', 'welBot'].forEach(id => {

        const el = document.getElementById(id);

        if (!el) return;

        el.innerHTML =
            '<option value="">Select Discord Bot</option>' +

            activeBots.map(bot => `
                <option value="${bot.id}">
                    ${bot.name}
                </option>
            `).join('');
    });
}

// ===== LOGS =====

async function loadLogs() {

    const logs = await apiGet('/logs/?limit=10');

    if (!logs) return;

    const tbody =
        document.getElementById('logTableBody');

    if (!tbody) return;

    if (!logs.length) {

        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-cell">
                    No logs yet
                </td>
            </tr>
        `;

        return;
    }

    tbody.innerHTML = logs.map(log => {

        const bot =
            botsCache.find(b => b.id === log.bot_id);

        return `
            <tr>

                <td>
                    ${fmtDate(log.timestamp)}
                </td>

                <td>
                    ${bot ? esc(bot.name) : '-'}
                </td>

                <td>
                    ${esc(log.message).substring(0, 50)}
                </td>

                <td>
                    ${capitalize(log.level)}
                </td>

            </tr>
        `;

    }).join('');
}

// ===== AUTO REPLIES =====

async function loadAutoReplies() {

    const rules =
        await apiGet('/auto-reply/');

    if (!rules) return;

    const container =
        document.getElementById('autoReplyList');

    if (!container) return;

    if (!rules.length) {

        container.innerHTML = '';

        setText('statAutoReply', 0);

        return;
    }

    container.innerHTML = rules.map(rule => {

        const bot =
            botsCache.find(b => b.id === rule.bot_id);

        return `
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:10px;
                background:rgba(255,255,255,.03);
                border-radius:8px;
                margin-bottom:8px;
            ">

                <div>

                    <strong>
                        "${esc(rule.trigger_keyword)}"
                    </strong>

                    → ${esc(rule.response_text)}

                    <div style="
                        font-size:.72rem;
                        color:var(--text-muted);
                        margin-top:4px;
                    ">
                        ${bot ? bot.name : ''}
                    </div>

                </div>

                <button
                    class="btn btn-danger btn-sm"
                    onclick="deleteAutoReply(${rule.id})"
                >
                    ×
                </button>

            </div>
        `;

    }).join('');

    setText('statAutoReply', rules.length);
}

async function deleteAutoReply(id) {

    const ok =
        await apiDelete(`/auto-reply/${id}`);

    if (ok) {

        showToast('Rule deleted', 'success');

        loadAutoReplies();
    }
}



async function updateStats() {

    const stats =
        await apiGet('/tasks/stats');

    if (stats) {

        setText('statMessages', stats.done);

        setText(
            'statMsgSub',
            `${stats.done} Sent`
        );
    }

    const totalBots = botsCache.length;

    setText('statBots', totalBots);

    setText(
        'statBotsSub',
        `${totalBots} Active Bots`
    );
}



document.addEventListener('DOMContentLoaded', () => {

    loadBots();

    loadLogs();

    loadAutoReplies();

    // ===== ADD BOT =====

    document.getElementById('addBotForm')
        ?.addEventListener('submit', async e => {

            e.preventDefault();

            const data = {

                name: val('botName'),

                token: val('botToken')
            };

            if (
                !data.name ||
                !data.token
            ) {

                showToast(
                    'Fill all fields',
                    'error'
                );

                return;
            }

            const response =
                await apiPost('/bots/', data);

            if (response) {

                showToast(
                    'Bot added!',
                    'success'
                );

                e.target.reset();

                loadBots();
            }
        });



    document.getElementById('sendMessageForm')
        ?.addEventListener('submit', async e => {

            e.preventDefault();

            const data = {

                bot_id: +val('msgBot'),

                target_id: val('msgTarget'),

                message: val('msgContent')
            };

            if (
                !data.bot_id ||
                !data.target_id ||
                !data.message
            ) {

                showToast(
                    'Fill all fields',
                    'error'
                );

                return;
            }

            const response =
                await apiPost(
                    '/tasks/send-message',
                    data
                );

            if (response) {

                showToast(
                    'Message queued!',
                    'success'
                );

                e.target.reset();

                loadLogs();

                updateStats();
            }
        });



    document.getElementById('autoReplyForm')
        ?.addEventListener('submit', async e => {

            e.preventDefault();

            const data = {

                bot_id: +val('arBot'),

                trigger_keyword: val('arKeyword'),

                response_text: val('arResponse'),

                match_type: 'contains'
            };

            if (
                !data.bot_id ||
                !data.trigger_keyword ||
                !data.response_text
            ) {

                showToast(
                    'Fill all fields',
                    'error'
                );

                return;
            }

            const response =
                await apiPost('/auto-reply/', data);

            if (response) {

                showToast(
                    'Rule added!',
                    'success'
                );

                e.target.reset();

                loadAutoReplies();
            }
        });



    document.getElementById('welcomeForm')
        ?.addEventListener('submit', async e => {

            e.preventDefault();

            const data = {

                bot_id: +val('welBot'),

                channel_id: val('welChannel'),

                message_template: val('welMessage')
            };

            if (
                !data.bot_id ||
                !data.channel_id ||
                !data.message_template
            ) {

                showToast(
                    'Fill all fields',
                    'error'
                );

                return;
            }

            const response =
                await apiPost('/welcome/', data);

            if (response) {

                showToast(
                    'Welcome message saved!',
                    'success'
                );

                e.target.reset();
            }
        });

    setInterval(() => {

        loadLogs();

        updateStats();

    }, 10000);
});