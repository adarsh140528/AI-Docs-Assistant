// ============================================================================
// AI-Docs-Assistant - Clean, Minimalist Frontend Logic
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
    // State
    const state = {
        knowledgeBases: [],
        selectedKBs: [],
        messages: [],
        isStreaming: false,
        uploadedFiles: []
    };

    // DOM Elements
    const kbListEl = document.getElementById("kb-list");
    const kbCountBadge = document.getElementById("kb-count-badge");
    const chatThreadEl = document.getElementById("chat-thread");
    const heroWelcomeEl = document.getElementById("hero-welcome");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const btnSend = document.getElementById("btn-send");
    
    // Ingestion Modal Elements
    const btnOpenIngest = document.getElementById("btn-open-ingest");
    const ingestModal = document.getElementById("ingest-modal");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const btnCancelModal = document.getElementById("btn-cancel-modal");
    const ingestForm = document.getElementById("ingest-form");
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const fileListPreview = document.getElementById("file-list-preview");
    const kbNameInput = document.getElementById("kb-name-input");
    const ingestProgressContainer = document.getElementById("ingest-progress-container");
    const ingestProgressBar = document.getElementById("ingest-progress-bar");
    const ingestProgressText = document.getElementById("ingest-progress-text");
    const btnSubmitIngest = document.getElementById("btn-submit-ingest");

    // Drawer Elements
    const sourceDrawer = document.getElementById("source-drawer");
    const btnCloseDrawer = document.getElementById("btn-close-drawer");
    const drawerDocTitle = document.getElementById("drawer-doc-title");
    const drawerPageTag = document.getElementById("drawer-page-tag");
    const drawerKbName = document.getElementById("drawer-kb-name");
    const drawerTextContent = document.getElementById("drawer-text-content");
    const btnCopySource = document.getElementById("btn-copy-source");

    // Footer buttons
    const btnClearChat = document.getElementById("btn-clear-chat");
    const btnExportChat = document.getElementById("btn-export-chat");

    // ------------------------------------------------------------------------
    // Initialization
    // ------------------------------------------------------------------------
    marked.setOptions({
        highlight: function(code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                return hljs.highlight(code, { language: lang }).value;
            }
            return hljs.highlightAuto(code).value;
        },
        breaks: true
    });

    fetchKnowledgeBases();

    // ------------------------------------------------------------------------
    // API & Data Fetching
    // ------------------------------------------------------------------------
    async function fetchKnowledgeBases() {
        try {
            const res = await fetch("/api/knowledge-bases");
            if (!res.ok) {
                console.warn(`Could not fetch knowledge bases (status: ${res.status})`);
                return;
            }
            const data = await res.json();
            state.knowledgeBases = data.knowledge_bases || [];
            
            // Auto-select first KB if none selected
            if (state.selectedKBs.length === 0 && state.knowledgeBases.length > 0) {
                state.selectedKBs = [state.knowledgeBases[0].name];
            }
            
            renderKBList();
        } catch (e) {
            console.error("Error fetching KBs:", e);
        }
    }

    function renderKBList() {
        if (kbCountBadge) kbCountBadge.textContent = state.knowledgeBases.length;

        if (state.knowledgeBases.length === 0) {
            kbListEl.innerHTML = `<div class="kb-empty-state">No knowledge bases yet. Click "Upload Documents" to create one.</div>`;
            return;
        }

        kbListEl.innerHTML = "";
        state.knowledgeBases.forEach(kb => {
            const isChecked = state.selectedKBs.includes(kb.name);
            const card = document.createElement("div");
            card.className = `kb-card ${isChecked ? "active" : ""}`;
            
            const docsCount = kb.documents ? kb.documents.length : 1;
            const pagesCount = kb.pages || 0;

            card.innerHTML = `
                <div class="kb-checkbox-row">
                    <input type="checkbox" class="kb-checkbox" ${isChecked ? "checked" : ""} data-kb="${kb.name}">
                    <div class="kb-info">
                        <span class="kb-name" title="${kb.name}">📚 ${kb.name}</span>
                        <span class="kb-meta">${docsCount} doc(s) • ${pagesCount} pages</span>
                    </div>
                </div>
                <button class="kb-del-btn" title="Delete" data-kb="${kb.name}">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                </button>
            `;

            // Checkbox toggle
            const checkbox = card.querySelector(".kb-checkbox");
            checkbox.addEventListener("change", (e) => {
                const kbName = e.target.getAttribute("data-kb");
                if (e.target.checked) {
                    if (!state.selectedKBs.includes(kbName)) state.selectedKBs.push(kbName);
                } else {
                    state.selectedKBs = state.selectedKBs.filter(name => name !== kbName);
                }
                renderKBList();
            });

            // Delete action
            const delBtn = card.querySelector(".kb-del-btn");
            delBtn.addEventListener("click", async (e) => {
                e.stopPropagation();
                const kbName = delBtn.getAttribute("data-kb");
                if (confirm(`Delete Knowledge Base "${kbName}"?`)) {
                    await deleteKnowledgeBase(kbName);
                }
            });

            kbListEl.appendChild(card);
        });
    }

    async function deleteKnowledgeBase(name) {
        try {
            await fetch(`/api/knowledge-bases/${name}`, { method: "DELETE" });
            state.selectedKBs = state.selectedKBs.filter(k => k !== name);
            await fetchKnowledgeBases();
        } catch (e) {
            alert("Failed to delete Knowledge Base");
        }
    }

    // ------------------------------------------------------------------------
    // Chat & Streaming Logic
    // ------------------------------------------------------------------------
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event("submit"));
        }
    });

    chatInput.addEventListener("input", () => {
        chatInput.style.height = "auto";
        chatInput.style.height = `${Math.min(chatInput.scrollHeight, 140)}px`;
    });

    // Starter Prompt Clicks
    document.querySelectorAll(".starter-card").forEach(card => {
        card.addEventListener("click", () => {
            const prompt = card.getAttribute("data-prompt");
            if (prompt) {
                chatInput.value = prompt;
                chatForm.dispatchEvent(new Event("submit"));
            }
        });
    });

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = chatInput.value.trim();
        if (!query || state.isStreaming) return;

        if (state.selectedKBs.length === 0) {
            alert("Please select or upload at least one Knowledge Base from the sidebar.");
            return;
        }

        // Hide Hero Welcome
        if (heroWelcomeEl) heroWelcomeEl.style.display = "none";

        // Append User Message
        appendMessage("user", query);
        chatInput.value = "";
        chatInput.style.height = "auto";

        // Create Assistant Bubble with cursor
        const assistantBubble = appendMessage("assistant", "", []);
        state.isStreaming = true;
        btnSend.disabled = true;

        let accumulatedAnswer = "";
        let sourcesList = [];

        try {
            const response = await fetch("/api/chat/stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: query,
                    history: state.messages.slice(-6),
                    indexes: state.selectedKBs
                })
            });

            if (!response.ok) {
                throw new Error("Chat request failed");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n\n");
                buffer = lines.pop();

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        const jsonStr = line.replace("data: ", "").trim();
                        if (!jsonStr) continue;

                        try {
                            const eventData = JSON.parse(jsonStr);

                            if (eventData.type === "sources") {
                                sourcesList = eventData.sources || [];
                            } else if (eventData.type === "token") {
                                accumulatedAnswer += eventData.content;
                                updateAssistantBubble(assistantBubble, accumulatedAnswer, true);
                            } else if (eventData.type === "error") {
                                accumulatedAnswer += `\n\n❌ ${eventData.error}`;
                                updateAssistantBubble(assistantBubble, accumulatedAnswer, false);
                            }
                        } catch (err) {
                            console.error("JSON parse error on stream chunk:", err);
                        }
                    }
                }
            }

            // Finalize bubble with sources
            updateAssistantBubble(assistantBubble, accumulatedAnswer, false, sourcesList);

            // Record in state
            state.messages.push({ role: "user", content: query });
            state.messages.push({ role: "assistant", content: accumulatedAnswer, sources: sourcesList });

        } catch (err) {
            updateAssistantBubble(assistantBubble, `❌ Error: ${err.message}`, false);
        } finally {
            state.isStreaming = false;
            btnSend.disabled = false;
        }
    });

    function appendMessage(role, content, sources = []) {
        const row = document.createElement("div");
        row.className = `message-row ${role === "user" ? "user-row" : "bot-row"}`;

        const avatar = document.createElement("div");
        avatar.className = `avatar ${role === "user" ? "user-avatar" : "bot-avatar"}`;
        avatar.innerHTML = role === "user" ? "👤" : "🤖";

        const bubble = document.createElement("div");
        bubble.className = `message-bubble ${role === "user" ? "user-bubble" : "bot-bubble"}`;

        if (role === "user") {
            bubble.textContent = content;
            row.appendChild(bubble);
            row.appendChild(avatar);
        } else {
            bubble.innerHTML = `<span class="typing-cursor"></span>`;
            row.appendChild(avatar);
            row.appendChild(bubble);
        }

        chatThreadEl.appendChild(row);
        chatThreadEl.scrollTop = chatThreadEl.scrollHeight;

        return bubble;
    }

    function updateAssistantBubble(bubble, markdownText, isTyping, sources = []) {
        let html = marked.parse(markdownText);
        if (isTyping) {
            html += `<span class="typing-cursor"></span>`;
        }

        bubble.innerHTML = html;

        // Render source pills if finalized
        if (!isTyping && sources && sources.length > 0) {
            const sourceContainer = document.createElement("div");
            sourceContainer.className = "sources-container";

            const seen = new Set();
            const uniqueSources = [];

            sources.forEach(s => {
                const key = `${s.source}_${s.page}`;
                if (!seen.has(key)) {
                    seen.add(key);
                    uniqueSources.push(s);
                }
            });

            uniqueSources.slice(0, 4).forEach(src => {
                const pill = document.createElement("button");
                pill.className = "source-pill-btn";
                pill.innerHTML = `📄 <b>${src.source || src.index}</b> • Page ${src.page}`;

                pill.addEventListener("click", () => {
                    openSourceDrawer(src.index || state.selectedKBs[0], src.source, src.page);
                });

                sourceContainer.appendChild(pill);
            });

            bubble.appendChild(sourceContainer);
        }

        chatThreadEl.scrollTop = chatThreadEl.scrollHeight;
    }

    // ------------------------------------------------------------------------
    // Source Page Inspector Drawer
    // ------------------------------------------------------------------------
    async function openSourceDrawer(index, source, page) {
        drawerDocTitle.textContent = source;
        drawerPageTag.textContent = `Page ${page}`;
        drawerKbName.textContent = `Knowledge Base: ${index}`;
        drawerTextContent.textContent = "Loading full page text...";
        sourceDrawer.classList.remove("hidden");

        try {
            const res = await fetch(`/api/page-preview?index=${encodeURIComponent(index)}&source=${encodeURIComponent(source)}&page=${page}`);
            const data = await res.json();
            drawerTextContent.textContent = data.text || "No text available for this page.";
        } catch (e) {
            drawerTextContent.textContent = "Could not load full page excerpt.";
        }
    }

    btnCloseDrawer.addEventListener("click", () => {
        sourceDrawer.classList.add("hidden");
    });

    sourceDrawer.addEventListener("click", (e) => {
        if (e.target === sourceDrawer) sourceDrawer.classList.add("hidden");
    });

    btnCopySource.addEventListener("click", () => {
        navigator.clipboard.writeText(drawerTextContent.textContent);
        btnCopySource.textContent = "Copied!";
        setTimeout(() => { btnCopySource.textContent = "Copy"; }, 2000);
    });

    // ------------------------------------------------------------------------
    // Ingestion Modal & Drag-and-Drop
    // ------------------------------------------------------------------------
    btnOpenIngest.addEventListener("click", () => {
        ingestModal.classList.remove("hidden");
        state.uploadedFiles = [];
        fileListPreview.innerHTML = "";
        ingestProgressContainer.classList.add("hidden");
        btnSubmitIngest.disabled = false;
    });

    const closeModal = () => ingestModal.classList.add("hidden");
    btnCloseModal.addEventListener("click", closeModal);
    btnCancelModal.addEventListener("click", closeModal);
    ingestModal.addEventListener("click", (e) => {
        if (e.target === ingestModal) closeModal();
    });

    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            handleFilesSelected(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            handleFilesSelected(fileInput.files);
        }
    });

    function handleFilesSelected(files) {
        state.uploadedFiles = Array.from(files);
        fileListPreview.innerHTML = "";
        state.uploadedFiles.forEach(f => {
            const item = document.createElement("div");
            item.className = "file-preview-item";
            item.innerHTML = `<span>📄 ${f.name}</span><span style="color: var(--text-muted);">${(f.size/1024/1024).toFixed(2)} MB</span>`;
            fileListPreview.appendChild(item);
        });
    }

    ingestForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (state.uploadedFiles.length === 0) {
            alert("Please select at least one document to upload.");
            return;
        }

        const formData = new FormData();
        state.uploadedFiles.forEach(f => {
            formData.append("files", f);
        });

        const customName = kbNameInput.value.trim();
        if (customName) {
            formData.append("custom_name", customName);
        }

        ingestProgressContainer.classList.remove("hidden");
        btnSubmitIngest.disabled = true;
        ingestProgressBar.style.width = "35%";
        ingestProgressText.textContent = "Parsing & Chunking...";

        setTimeout(() => {
            ingestProgressBar.style.width = "75%";
            ingestProgressText.textContent = "Generating Embeddings & Indexes...";
        }, 700);

        try {
            const res = await fetch("/api/ingest", {
                method: "POST",
                body: formData
            });

            if (!res.ok) {
                let errMsg = `Upload failed (Status ${res.status})`;
                try {
                    const err = await res.json();
                    errMsg = err.detail || err.message || errMsg;
                } catch (_) {
                    const text = await res.text();
                    if (text && text.length < 300 && !text.includes("<!DOCTYPE") && !text.includes("<html")) {
                        errMsg = text;
                    } else {
                        errMsg = `Server error (${res.status} ${res.statusText || "Processing Error"}). Please retry or check server logs.`;
                    }
                }
                throw new Error(errMsg);
            }

            const data = await res.json();
            ingestProgressBar.style.width = "100%";
            ingestProgressText.textContent = "Complete!";

            setTimeout(() => {
                closeModal();
                fetchKnowledgeBases();
                state.selectedKBs = [data.index];
                renderKBList();
            }, 500);

        } catch (err) {
            alert(`Error: ${err.message}`);
            ingestProgressContainer.classList.add("hidden");
            btnSubmitIngest.disabled = false;
        }
    });

    // ------------------------------------------------------------------------
    // Chat Actions (Clear & Export)
    // ------------------------------------------------------------------------
    btnClearChat.addEventListener("click", () => {
        if (confirm("Clear current conversation?")) {
            state.messages = [];
            chatThreadEl.innerHTML = "";
            if (heroWelcomeEl) {
                chatThreadEl.appendChild(heroWelcomeEl);
                heroWelcomeEl.style.display = "flex";
            }
        }
    });

    btnExportChat.addEventListener("click", () => {
        if (state.messages.length === 0) {
            alert("No conversation to export.");
            return;
        }

        let md = "# Adorush AI Conversation Transcript\n\n";
        state.messages.forEach(m => {
            md += `### ${m.role.toUpperCase()}:\n${m.content}\n\n---\n\n`;
        });

        const blob = new Blob([md], { type: "text/markdown" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "chat_transcript.md";
        a.click();
        URL.revokeObjectURL(url);
    });
});
