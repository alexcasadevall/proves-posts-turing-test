Qualtrics.SurveyEngine.addOnload(function() {
    
    var numBloc = 3; 
    
    var jsonUrl = Qualtrics.SurveyEngine.getEmbeddedData('URL_Post_' + numBloc);
    
    if (!jsonUrl) {
        document.getElementById('reddit-messages').innerHTML = "<p style='color:red;'>Error de Qualtrics: No s'ha rebut cap ruta de JSON des del Cervell.</p>";
        return;
    }

    const COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#0ea5e9', '#ec4899', '#8b5cf6'];
    
    fetch(jsonUrl)
        .then(response => {
            if (!response.ok) throw new Error("No s'ha trobat el fitxer a GitHub: " + jsonUrl);
            return response.json();
        })
        .then(data => {
            if (data.post_original) {
                document.getElementById('news-agency').innerText = data.post_original.agency;
                document.getElementById('news-title').innerText = data.post_original.title;
                document.getElementById('news-body').innerText = data.post_original.body;
                const postTime = new Date(data.post_original.timestamp * 1000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
                document.getElementById('news-time').innerText = postTime;
            }
            
            document.getElementById('p-count').innerText = data.num_participants + ' participants';
            
            const list = document.getElementById('reddit-messages');
            list.innerHTML = ''; 
            const userColors = {};
            let cIdx = 0;

            data.messages.forEach(m => {
                if(!userColors[m.sender]) { 
                    userColors[m.sender] = COLORS[cIdx % COLORS.length]; 
                    cIdx++; 
                }
                const col = userColors[m.sender];
                const replyCol = m.reply_to ? (userColors[m.reply_to] || '#cbd5e1') : null;

                const card = document.createElement('div');
                card.className = 'message-card';
                card.style.borderLeftColor = col;
                
                let quoteHtml = '';
                if (m.is_mention && m.reply_to) {
                    quoteHtml = `
                    <div class="quote" style="border-left-color: ${replyCol}">
                        <div class="quote-user" style="color: ${replyCol}">${m.reply_to}</div>
                        <div class="quote-text">${m.reply_text || "..."}</div>
                    </div>`;
                }
                
                const t = new Date(m.timestamp * 1000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
                
                card.innerHTML = `
                    <div class="msg-header">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <div class="av" style="background:${col}">${m.sender[0]}</div>
                            <span class="un" style="color:${col}">${m.sender}</span>
                        </div>
                        <span class="ts">${t}</span>
                    </div>
                    ${quoteHtml}
                    <div class="msg-body">${m.text}</div>
                    <div class="msg-footer">
                        <span class="btn"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" style="width:14px; height:14px; margin-bottom:-2px;"><path d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/></svg> Reply</span>
                        <span class="btn" style="${m.likes > 0 ? 'color:#ef4444' : ''}"><svg fill="${m.likes > 0 ? '#ef4444' : 'none'}" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" style="width:14px; height:14px; margin-bottom:-2px;"><path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg> ${m.likes > 0 ? m.likes : 'Like'}</span>
                        <span class="btn"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" style="width:14px; height:14px; margin-bottom:-2px;"><circle cx="12" cy="12" r="4"></circle><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-3.92 7.94"></path></svg> Mention</span>
                        <span class="btn"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" style="width:14px; height:14px; margin-bottom:-2px;"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"></path><line x1="4" y1="22" x2="4" y2="15"></line></svg> Report</span>
                    </div>`;
                
                list.appendChild(card);
            });
        })
        .catch(err => {
            document.getElementById('reddit-messages').innerHTML = `
            <div style="padding:20px; background:#fee2e2; border:1px solid #ef4444; border-radius:8px; color:#b91c1c;">
                <strong>Error descarregant la simulació:</strong> ${err.message}<br>
                <small>Assegura't que el fitxer està al GitHub a la ruta correcta.</small>
            </div>`;
        });
});