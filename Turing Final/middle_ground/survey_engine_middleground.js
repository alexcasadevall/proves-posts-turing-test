Qualtrics.SurveyEngine.addOnload(function() {

    var nextButton = document.getElementById('NextButton');
    if (nextButton) {
        nextButton.disabled = true;
        nextButton.style.opacity = '0.5';
        nextButton.style.cursor = 'not-allowed';
        nextButton.title = 'Si no puedes continuar, asegúrate de haber leído las 3 conversaciones hasta el final.';
    }

    var url1 = Qualtrics.SurveyEngine.getJSEmbeddedData('MG_URL_1');
    var url2 = Qualtrics.SurveyEngine.getJSEmbeddedData('MG_URL_2');
    var url3 = Qualtrics.SurveyEngine.getJSEmbeddedData('MG_URL_3');

    if (!url1 || !url2 || !url3) {
        document.getElementById('mg-news-title').innerHTML = 
            "<span style='color:#ef4444;'>Error: Falten dades del Cervell. Intenta recarregar la pàgina.</span>";
        return;
    }

    var urls = [url1, url2, url3];
    var COLORS = ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#6366f1'];

    Promise.all(urls.map(function(u) { return fetch(u).then(function(r) { return r.json(); }); }))
        .then(function(dataArray) {
            
            var baseData = dataArray[0];
            if (baseData.post_original) {
                document.getElementById('mg-news-agency').innerText = baseData.post_original.agency || '';
                document.getElementById('mg-news-title').innerText = baseData.post_original.title || '';
                document.getElementById('mg-news-body').innerText = baseData.post_original.body || '';
            }

            var scrollStatus = { 1: false, 2: false, 3: false };

            function checkAllScrolled() {
                if (scrollStatus[1] && scrollStatus[2] && scrollStatus[3]) {
                    if (nextButton) {
                        nextButton.disabled = false;
                        nextButton.style.opacity = '1';
                        nextButton.style.cursor = 'pointer';
                        nextButton.title = '';
                    }
                }
            }

            dataArray.forEach(function(data, index) {
                var forumNum = index + 1;
                var list = document.getElementById('reddit-messages-' + forumNum);
                list.innerHTML = '';

                var userColors = {};
                var cIdx = 0;

                data.messages.forEach(function(m) {
                    if (!userColors[m.sender]) {
                        userColors[m.sender] = COLORS[cIdx % COLORS.length];
                        cIdx++;
                    }
                    var col = userColors[m.sender];
                    var replyCol = m.reply_to ? (userColors[m.reply_to] || '#94a3b8') : null;

                    var card = document.createElement('div');
                    card.style.cssText = 'background:white;border:1px solid #e2e8f0;border-left:4px solid ' + col + ';border-radius:12px;padding:12px;margin-bottom:10px;font-family:Inter,sans-serif;';

                    var headerHtml = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">' +
                        '<div style="display:flex;align-items:center;gap:8px;">' +
                        '<div style="width:28px;height:28px;border-radius:50%;background:' + col + ';color:white;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0;">' + m.sender[0].toUpperCase() + '</div>' +
                        '<span style="font-size:14px;font-weight:600;color:' + col + ';">' + m.sender + '</span>' +
                        '</div>' +
                        '</div>';

                    var quoteHtml = '';
                    if (m.reply_to && m.reply_text) {
                        var truncated = m.reply_text.length > 50 ? m.reply_text.substring(0, 50) + '...' : m.reply_text;
                        quoteHtml = '<div style="margin:0 0 8px 0;padding:6px 10px;background:#f8fafc;border-left:3px solid ' + (replyCol || '#94a3b8') + ';border-radius:4px;">' +
                            '<div style="font-size:11px;font-weight:600;color:' + (replyCol || '#94a3b8') + ';margin-bottom:2px;">' + m.reply_to + '</div>' +
                            '<div style="font-size:11px;color:#64748b;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' + truncated + '</div>' +
                            '</div>';
                    }

                    var bodyHtml = '<div style="font-size:13px;line-height:1.5;color:#1e293b;margin-bottom:8px;">' + m.text + '</div>';

                    card.innerHTML = headerHtml + quoteHtml + bodyHtml;
                    list.appendChild(card);
                });

                setTimeout(function() {
                    var wrapper = document.getElementById('session-wrapper-' + forumNum);
                    
                    if (wrapper.scrollHeight <= wrapper.clientHeight + 10) {
                        scrollStatus[forumNum] = true;
                        checkAllScrolled();
                    } else {
                        wrapper.addEventListener('scroll', function scrollCheck() {
                            if (wrapper.scrollHeight - wrapper.scrollTop <= wrapper.clientHeight + 30) {
                                scrollStatus[forumNum] = true;
                                checkAllScrolled();
                                wrapper.removeEventListener('scroll', scrollCheck);
                            }
                        });
                    }
                }, 300);
            });
        })
        .catch(function(err) {
            document.getElementById('mg-news-title').innerHTML =
                '<span style="color:#b91c1c;">Error: No s\'han pogut carregar els fòrums. Verifica la connexió.</span>';
        });
});