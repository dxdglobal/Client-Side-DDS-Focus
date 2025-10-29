// Çalışma/Toplantı mod yönetimi
let currentMode = 'work'; // 'work' veya 'meeting'
let meetingRecords = [];

function setMode(mode) {
    // Eğer timer çalışıyorsa mod değiştirmeye izin verme
    if (isTimerRunning) {
        const lang = sessionStorage.getItem('selectedLanguage') || 'en';
        const message = lang === 'tr' 
            ? "⛔ Zamanlayıcı çalışırken mod değiştiremezsiniz. Lütfen önce görevi bitirin."
            : "⛔ You cannot change mode while timer is running. Please finish your task first.";
        showToast(message, "error");
        return;
    }
    
    currentMode = mode;
    const workBtn = document.getElementById('workModeBtn');
    const meetingBtn = document.getElementById('meetingModeBtn');
    
    if (mode === 'work') {
        workBtn.classList.add('active');
        workBtn.style.background = '#006039';
        workBtn.style.color = '#fff';
        meetingBtn.classList.remove('active');
        meetingBtn.style.background = '#fff';
        meetingBtn.style.color = '#006039';
        setState('work');
        
        // Çalışma modunda dropdown'ları göster
        document.getElementById('projectSection').style.display = 'block';
        document.getElementById('taskSection').style.display = 'block';

            // Eğer görev seçiliyse başlat butonunu enable et
            const taskSelect = document.getElementById('task');
            const startBtn = document.getElementById('startBtn');
            if (taskSelect && startBtn) {
                const selectedTaskOption = taskSelect.options[taskSelect.selectedIndex];
                if (taskSelect.value && !selectedTaskOption.disabled) {
                    startBtn.disabled = false;
                    startBtn.style.backgroundColor = 'green';
                } else {
                    startBtn.disabled = true;
                    startBtn.style.backgroundColor = 'gray';
                }
            }
    } else {
        meetingBtn.classList.add('active');
        meetingBtn.style.background = '#006039';
        meetingBtn.style.color = '#fff';
        workBtn.classList.remove('active');
        workBtn.style.background = '#fff';
        workBtn.style.color = '#006039';
        setState('meeting');
        
        // Toplantı modunda dropdown'ları gizle
        document.getElementById('projectSection').style.display = 'none';
        document.getElementById('taskSection').style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const workBtn = document.getElementById('workModeBtn');
    const meetingBtn = document.getElementById('meetingModeBtn');
    if (workBtn && meetingBtn) {
        workBtn.addEventListener('click', () => setMode('work'));
        meetingBtn.addEventListener('click', () => setMode('meeting'));
    }

    // Screenshot interval fetch
    fetchScreenshotInterval();
});

// Screenshot interval fetch and display
function fetchScreenshotInterval() {
    const intervalDiv = document.getElementById('screenshotInterval');
    if (!user || !intervalDiv) return;
    
    fetch('/api/get-staff-screen-shot-time', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: user.email, staff_id: user.staffid })
    })
    .then(res => res.json())
    .then(data => {
        if (data && data.interval) {
            intervalDiv.textContent = `${data.interval} seconds`;
        } else {
            intervalDiv.textContent = 'N/A';
        }
    })
    .catch(() => {
        intervalDiv.textContent = 'N/A';
    });
}

let isStartInProgress = false;
let isSubmitInProgress = false;
let isResetInProgress = false;
let idleTriggerTime = 0;
let idleTimeout = 5;

// 🎨 DDS Styling API Integration for Client Page
const translations = {
    en: {
        welcome: "Welcome...",
        logging: "Logging",
        total: "Total Time Count",
        loadingTasks: "Loading tasks...",
        idleTitle: "⏸️ You're Idle",
        idleDesc: "You've been inactive. Timer is paused.",
        min: "min", 
        today: "Today",
        work: "WORK",
        meeting: "MEETING",
        start: "START",
        finish: "Finish",
        hrs: "HRS",
        min: "MIN",
        sec: "SEC",
        modalTitle: "📝 Task Completion",
        meetingModalTitle: "📝 Meeting Completion",
        modalDesc: "Please describe what you have completed for this task:",
        meetingModalDesc: "Please describe what was discussed in this meeting:",
        submit: "Submit",
        selectTask: "-- Select a Task --",
        loadingProjects: "Loading projects...",
        user: "User",
        project: "Project",
        task: "Task",
        client: "Staff",
        modalPlaceholder: "Type your task details here...",
        meetingModalPlaceholder: "Type your meeting notes here...",
        selectProject: "Select a Project",
        minWorkWarning: "⚠️ You must work at least 1 minute to finish a task.",
        logout: "Logout",
        logoutTitle: "🔒 Confirm Logout",
        logoutDesc: "Are you sure you want to log out from DDS-FocusPro?",
        logoutConfirm: "Logout",
        logoutCancel: "Cancel",
        feedbackTitle: "💬 Share Your Feedback",
        feedbackDesc: "We'd love to hear your thoughts about DDSFocusPro:",
        feedbackPlaceholder: "Type your feedback here...",
        feedbackSubmit: "Submit Review",
        navDashboard: "DASHBOARD",
        navHelp: "HELP",
        navSettings: "SETTINGS",
        statusText: {
            work: " ",
            break: "You are on a BREAK – Relax and recharge ☕",
            idle: " ",
            meeting: "In a MEETING – Stay connected and engaged 👥"
        },
        navFeedback: "FEEDBACK",
        rememberMe: "Remember Me",
        selectMode: "Select Mode",
        workMode: "Work Mode",
        meetingMode: "Meeting Mode",
        totalLogged: "Total Time Logged",
        screenRecording: "Screen Recording",
        screenshotInterval: "Screenshot Interval"
    },
    tr: {
        welcome: "Hoş geldin...",
        logging: "Ekran Kaydı",
        total: "Toplam Süre",
        minWorkWarning: "⚠️ Bir görevi bitirmek için en az 1 dakika çalışmalısınız.",
        idle: "BOŞTA",
        break: "MOLA",
        min: "dk",
        meeting: "TOPLANTI",
        today: "Tarih",
        work: "ÇALIŞMA",
        start: "BAŞLAT",
        finish: "Bitir",
        hrs: "SA",
        min: "DK",
        sec: "SN",
        modalTitle: "📝 İş Tamamlandı",
        meetingModalTitle: "📝 Toplantı Tamamlandı",
        modalDesc: "Bu İş Emri için ne yaptığınızı açıklayın:",
        meetingModalDesc: "Bu toplantıda neler konuşulduğunu açıklayın:",
        submit: "Gönder",
        selectTask: "-- İş Emri Seçin --",
        loadingProjects: "Projeler yükleniyor...",
        user: "Kullanıcı",
        project: "Proje",
        task: "İş Emri",
        client: "Personel",
        modalPlaceholder: "İş Emri detaylarını buraya yazın...",
        meetingModalPlaceholder: "Toplantı notlarını buraya yazın...",
        selectProject: "Proje Seçin",
        logout: "Çıkış Yap",
        logoutTitle: "🔒 Çıkış Onayı",
        logoutDesc: "DDS-FocusPro'dan çıkmak istediğinize emin misiniz?",
        logoutConfirm: "Çıkış Yap",
        logoutCancel: "İptal",
        feedbackTitle: "💬 Geri Bildirim Gönder",
        feedbackDesc: "DDSFocusPro hakkında görüşlerinizi duymak isteriz:",
        feedbackPlaceholder: "Geri bildiriminizi buraya yazın...",
        feedbackSubmit: "Gönder",
        navDashboard: "PANO",
        navHelp: "YARDIM",
        navSettings: "AYARLAR",
        navFeedback: "GERİ BİLDİRİM",
        statusText: {
            work: " ",
            break: "Şu anda MOLA'dasınız – Rahatlayın ve enerji toplayın ☕",
            idle: " ",
            meeting: "Şu anda TOPLANTIDASINIZ – İletişimde ve odaklı kalın 👥"
        },
        rememberMe: "Beni Hatırla",
        selectMode: "Mod Seçin",
        workMode: "Çalışma Modu",
        meetingMode: "Toplantı Modu",
        totalLogged: "Toplam Zaman",
        screenRecording: "Ekran Kaydı",
        screenshotInterval: "Ekran Görüntüsü Aralığı"
    }
};

function showToast(message, type = 'success') {
    Toastify({
        text: message,
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: type === 'error' ? "#e74c3c" : "#27ae60",
        close: true
    }).showToast();
}

function logout() {
    sessionStorage.clear();
    window.location.href = '/';
}

function updateDrawerContent(projectName, taskName, isMeeting = false) {
    const drawerProjectName = document.getElementById('drawerProjectName');
    const drawerProjectDesc = document.getElementById('drawerProjectDesc');
    
    if (drawerProjectName) {
        if (isMeeting) {
            drawerProjectName.textContent = 'Meeting Session';
            if (drawerProjectDesc) {
                drawerProjectDesc.textContent = 'Currently in a meeting';
            }
        } else {
            drawerProjectName.textContent = projectName || 'No Project Selected';
            if (drawerProjectDesc) {
                drawerProjectDesc.textContent = `Working on: ${projectName || 'No project selected'}`;
            }
        }
    }
    
    const drawerTaskName = document.getElementById('drawerTaskName');
    const drawerTaskDesc = document.getElementById('drawerTaskDesc');
    
    if (drawerTaskName) {
        if (isMeeting) {
            drawerTaskName.textContent = 'Meeting';
            if (drawerTaskDesc) {
                drawerTaskDesc.textContent = 'Meeting in progress';
            }
        } else {
            drawerTaskName.textContent = taskName || 'No Task Selected';
            if (drawerTaskDesc) {
                drawerTaskDesc.textContent = `Current task: ${taskName || 'No task selected'}`;
            }
        }
    }
    
    const drawerSessionStart = document.getElementById('drawerSessionStart');
    if (drawerSessionStart) {
        drawerSessionStart.textContent = new Date().toLocaleTimeString();
    }
}

let timerInterval, totalSeconds = 0;
let isTimerRunning = false;
let currentTaskId = null, sessionStartTime = null;
let selectedProjectName = '', selectedTaskName = '', user = null;

window.onload = function () {
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';
    applyClientLanguage(lang);
    const todayDateField = document.getElementById('todayDate');
    const today = new Date();
    todayDateField.value = today.toLocaleDateString('en-CA');    

    user = JSON.parse(sessionStorage.getItem('user'));
    if (user) {
        document.getElementById('displayUserName').innerText = user.firstName;
        document.getElementById('clientNameInput').value = user.firstName;
        const profileImg = document.getElementById('profileImage');
        const imgUrl = `https://crm.deluxebilisim.com/uploads/staff_profile_images/${user.staffid}/small_${user.profileImage}`;
        profileImg.src = imgUrl;
        profileImg.onerror = function () {
            this.onerror = null;
            this.src = "../static/images/user_placeholder.png";
        };

        fetchAIProjects(user);
        saveUserProjectsToCache(user);
    }

    setTimeout(() => {
        console.log('🔄 Client.js: Re-applying styling after DOM setup...');
    }, 1000);
};

let idleCountdownInterval;

setInterval(() => {
    if (!isTimerRunning) return;
    
    // Toplantı modunda idle kontrolü yapma
    if (currentMode === 'meeting') return;

    fetch('/check_idle_state')
        .then(res => res.json())
        .then(data => {
            if (data.idle) {
                console.log("🛑 Backend says: User is idle");
                idleTriggerTime = Date.now();
                pauseTimer();
                resetTimer();
                setState('idle');

                const idleModal = document.getElementById("idleModal");
                const countdownText = document.getElementById("idleCountdownText");
                const counterSpan = document.getElementById("idleCounter");

                if (idleModal && countdownText && counterSpan) {
                    idleModal.style.display = 'flex';
                    const idleContent = idleModal.querySelector(".modal-content");
                    idleContent.classList.remove('idle-shake');
                    void idleContent.offsetWidth;
                    idleContent.classList.add('idle-shake');

                    setTimeout(() => {
                        handleAutoIdleSubmit();
                    }, 5000);
                }
            }
        })
        .catch(console.error);
}, 10000);

async function handleAutoIdleSubmit() {
    stopScreenRecording();
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';

    const totalIdleSeconds = 180;
    const actualEndTime = Math.floor(idleTriggerTime / 1000);
    const adjustedEndTime = actualEndTime - totalIdleSeconds;
    const durationWorked = adjustedEndTime - sessionStartTime;

    const minsWorked = durationWorked >= 60 ? Math.floor(durationWorked / 60) : 0;
    const secsWorked = durationWorked % 60;
    const idleMsg = lang === 'tr'
    ? (minsWorked === 0
        ? `Kullanıcı 1 dakikadan az çalıştı ve ${totalIdleSeconds} saniye boşta kaldı.`
        : `Kullanıcı ${minsWorked} dakika çalıştı ve ${totalIdleSeconds} saniye boşta kaldı.`)
    : (minsWorked === 0
        ? `User worked for less than 1 minute and stayed idle for ${totalIdleSeconds} seconds.`
        : `User worked for ${minsWorked} minutes and stayed idle for ${totalIdleSeconds} seconds.`);

    document.getElementById('totaltimecount').innerText = `${minsWorked} min`;

    console.log("📤 Auto-submitting due to idle...");
    console.log({
        email: user.email,
        task: currentTaskId,
        start: sessionStartTime,
        adjustedEndTime,
        idleMsg
    });

    try {
        await fetch('/end_task_session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: user.email,
                staff_id: String(user.staffid),
                task_id: currentTaskId,
                end_time: adjustedEndTime,
                note: idleMsg
            })
        });

        resetTimer();
        stopScreenRecording();
        stopDailyLogsCapture();
        showToast('✅ Auto-saved due to idle', 'success');
    } catch (error) {
        console.error("❌ Failed to auto-save:", error);
    }
}

document.getElementById('startBtn').addEventListener('click', function () {
    // Çalışma modunda task seçimini kontrol et
    if (currentMode === 'work') {
        const taskSelect = document.getElementById('task');
        const selectedTaskOption = taskSelect.options[taskSelect.selectedIndex];
        const taskId = taskSelect.value;

        if (!taskId || taskId === "" || selectedTaskOption.disabled) {
            showToast('⚠️ Please select a task first!', 'error');
            return;
        }
        currentTaskId = taskId;
        selectedProjectName = document.getElementById('project').selectedOptions[0]?.textContent || '';
        selectedTaskName = selectedTaskOption.textContent;
    } else {
        // Toplantı modunda
        currentTaskId = 'meeting';
        selectedProjectName = 'Meeting';
        selectedTaskName = 'Meeting Session';
    }

    if (!isTimerRunning) {
        sessionStartTime = Math.floor(Date.now() / 1000);

        updateDrawerContent(selectedProjectName, selectedTaskName, currentMode === 'meeting');

        fetch('/start_screen_recording', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: user.email,
                project: selectedProjectName,
                task: selectedTaskName
            })
        }).catch(console.error);

        startDailyLogsCapture();
        startTimer();
        setState(currentMode === 'meeting' ? 'meeting' : 'work');

        // Başlat tuşunu disabled yap
        const startBtn = document.getElementById('startBtn');
        if (startBtn) {
            startBtn.disabled = true;
            startBtn.style.backgroundColor = 'gray';
        }

        setTimeout(() => {
        }, 500);
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            console.log('🔄 Reset button clicked');
            console.log('⏱️ Total seconds:', totalSeconds);
            
            if (totalSeconds < 10) {
                console.log('⚠️ Session too short, showing warning');
                const lang = sessionStorage.getItem('selectedLanguage') || 'en';
                const message = translations[lang].minWorkWarning;
                showToast(message, 'error');
                return;
            }
            
            console.log('✅ Opening finish modal');
            openModal();
        });
        console.log('✅ Reset button event listener attached');
    } else {
        console.error('❌ resetBtn element not found!');
    }
});

function startTimer() {
    sessionStartTime = Math.floor(Date.now() / 1000);
    
    if (currentMode === 'work') {
        console.log("📤 Sending to /start_task_session:");
        console.log({
            email: user.email,
            staff_id: String(user.staffid),
            task_id: currentTaskId,
            start_time: sessionStartTime
        });

        fetch('/start_task_session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: user.email,
                staff_id: String(user.staffid),
                task_id: currentTaskId,
                start_time: sessionStartTime
            })
        })
        .then(res => res.json())
        .then(data => {
            console.log("📤 Sent start time:", sessionStartTime);
            console.log("📤 Sent task ID   :", currentTaskId);
            console.log("📤 Sent staff ID  :", user.staffid);
            console.log("📥 Server response:", data);
        })
        .catch(console.error);
    }

    isTimerRunning = true;
    document.getElementById('startBtn').disabled = true;
    document.getElementById('startBtn').style.backgroundColor = 'gray';
    
    // Sadece çalışma modunda dropdown'ları disable et
    if (currentMode === 'work') {
        document.getElementById('project').disabled = true;
        document.getElementById('task').disabled = true;
    }
    
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';
    document.getElementById('loggingInput').value = lang === 'tr' ? 'EVET' : 'YES';

    timerInterval = setInterval(updateTimerDisplay, 1000);
}

function pauseTimer() {
    console.log("Timer paused, seconds was:", totalSeconds);
    clearInterval(timerInterval);
    isTimerRunning = false;
    document.getElementById('startBtn').disabled = false;
    document.getElementById('startBtn').style.backgroundColor = 'green';
}

function resetTimer() {
    clearInterval(timerInterval);
    totalSeconds = 0;
    isTimerRunning = false;

    document.getElementById('hours').innerText = '00';
    document.getElementById('minutes').innerText = '00';
    document.getElementById('seconds').innerText = '00';

    document.getElementById('startBtn').disabled = false;
    document.getElementById('startBtn').style.backgroundColor = 'green';

    // Sadece çalışma modunda dropdown'ları enable et
    if (currentMode === 'work') {
        const projectSelect = document.getElementById('project');
        const taskSelect = document.getElementById('task');
        projectSelect.disabled = false;
        taskSelect.disabled = false;
    }

    const lang = sessionStorage.getItem('selectedLanguage') || 'en';
    document.getElementById('loggingInput').value = lang === 'tr' ? 'HAYIR' : 'NO';
    document.getElementById('totaltimecount').innerText = `0 min 0 sec`;
}

function updateTimerDisplay() {
    totalSeconds++;

    document.getElementById('hours').innerText = String(Math.floor(totalSeconds / 3600)).padStart(2, '0');
    document.getElementById('minutes').innerText = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0');
    document.getElementById('seconds').innerText = String(totalSeconds % 60).padStart(2, '0');

    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';

    const labelMin = translations[lang].min || 'min';
    const labelSec = translations[lang].sec || 'sec';

    document.getElementById('totaltimecount').innerText = `${mins} ${labelMin} ${secs} ${labelSec}`;
}

function stopScreenRecording() {
    fetch('/stop_screen_recording', { method: 'POST' })
        .then(res => res.json())
        .catch(console.error);
}

let dailyLogsInterval;

function startDailyLogsCapture() {
    console.log("📋 Starting automatic daily logs capture...");
    
    captureCurrentActivityLog();
    
    dailyLogsInterval = setInterval(() => {
        captureCurrentActivityLog();
    }, 60000);
}

function stopDailyLogsCapture() {
    if (dailyLogsInterval) {
        console.log("🛑 Stopping daily logs capture...");
        clearInterval(dailyLogsInterval);
        dailyLogsInterval = null;
    }
}

function captureCurrentActivityLog() {
    if (!user || !currentTaskId) return;
    
    const currentTime = new Date().toISOString();
    const logData = {
        email: user.email,
        staff_id: user.staffid,
        task_id: currentTaskId,
        project_name: selectedProjectName,
        task_name: selectedTaskName,
        timestamp: currentTime,
        activity_type: isTimerRunning ? (currentMode === 'meeting' ? 'meeting' : 'working') : 'idle',
        timer_seconds: totalSeconds
    };
    
    fetch('/capture_activity_log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            console.log("📋 Activity log captured successfully");
        }
    })
    .catch(err => console.error("❌ Failed to capture activity log:", err));
}

function fetchAIProjects(user) {
    const projectSelect = document.getElementById('project');
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';
    const t = {
        en: { loadingProjects: "Loading projects..." },
        tr: { loadingProjects: "Projeler yükleniyor..." }
    };
    projectSelect.innerHTML = `<option disabled selected>${t[lang].loadingProjects}</option>`;

    fetch('/get_ai_filtered_projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: user.email, username: `${user.firstName} ${user.lastName || ''}` })
    })
        .then(response => response.json())
        .then(data => {
            const projects = data.projects || [];
            projectSelect.innerHTML = '';
            const lang = sessionStorage.getItem('selectedLanguage') || 'en';
            const t = {
                en: { selectProject: "Select a Project" },
                tr: { selectProject: "Proje Seçin" }
            };
            const defaultOption = new Option(t[lang].selectProject, '');
            projectSelect.appendChild(defaultOption);
            
            const uniqueProjects = [];
            const seenKeys = new Set();

            projects.forEach(project => {
                if (!seenKeys.has(project.id)) {
                    seenKeys.add(project.id);
                    uniqueProjects.push(project);
                }
            });

            uniqueProjects.forEach(project => {
                const option = new Option(project.name || project.projectname || 'Unnamed Project', project.id);
                projectSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error(error);
            showToast('❌ Error loading projects', 'error');
        });
}

function loadTasksForProject() {
    const projectId = document.getElementById('project').value;
    const taskSelect = document.getElementById('task');
    const lang = sessionStorage.getItem('selectedLanguage') || 'tr';
    const selectTaskText = lang === 'tr' ? '-- İş Emri Seçin --' : '-- Select a Task --';
    const loadingTasksText = lang === 'tr' ? 'Görevler yükleniyor...' : 'Loading tasks...';
    
    if (!projectId) {
        taskSelect.innerHTML = `<option disabled selected>${selectTaskText}</option>`;
        return;
    }

    taskSelect.innerHTML = `<option disabled selected>${loadingTasksText}</option>`;

    fetch(`/get_tasks/${projectId}`)
        .then(response => response.json())
        .then(data => {
            taskSelect.innerHTML = '';
            const placeholder = new Option(selectTaskText, '');
            placeholder.disabled = true;
            placeholder.selected = true;
            taskSelect.appendChild(placeholder);

            const tasks = data.tasks || [];
            tasks.forEach(task => {
                const option = new Option(task.name || task.subject || 'Unnamed Task', task.id);
                taskSelect.appendChild(option);
            });

            console.log(`📋 Loaded ${tasks.length} tasks for project ${projectId}:`);
            tasks.forEach(task => {
                console.log(`🧾 [Task] ID: ${task.id} | Name: ${task.name} | Status: ${task.status}`);
            });
        })
        .catch(error => {
            console.error("❌ Error loading tasks:", error);
            taskSelect.innerHTML = '<option disabled>Error loading tasks</option>';
        });
}

function saveUserProjectsToCache(user) {
    fetch('/cache_user_projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: user.email, username: user.firstName, projects: user.projects })
    }).then(response => response.json()).catch(console.error);
}

function fetchLoggedTaskTimes() {
    fetch(`/get_task_time_summary/${user.email}`)
        .then(res => res.json())
        .then(data => {
        })
        .catch(err => console.error("❌ Error loading task times:", err));
}

function openModal() {
    console.log('🎯 openModal() called');
    const modal = document.getElementById('finishModal');
    console.log('📋 Modal element:', modal);
    
    if (!modal) {
        console.error('❌ finishModal not found!');
        return;
    }
    
    // Modal içeriğini moda göre güncelle
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';
    if (currentMode === 'meeting') {
        document.getElementById('modalTitle').textContent = translations[lang].meetingModalTitle;
        document.getElementById('modalDesc').textContent = translations[lang].meetingModalDesc;
        document.getElementById('taskDetailInput').placeholder = translations[lang].meetingModalPlaceholder;
    } else {
        document.getElementById('modalTitle').textContent = translations[lang].modalTitle;
        document.getElementById('modalDesc').textContent = translations[lang].modalDesc;
        document.getElementById('taskDetailInput').placeholder = translations[lang].modalPlaceholder;
    }
    
    modal.style.display = 'flex';
    console.log('👁️ Modal display set to flex');
    
    setTimeout(() => {
        modal.classList.remove('hide');
        modal.classList.add('show');
        console.log('🎬 Modal animation classes applied');
    }, 10);
    
    const loggingInput = document.getElementById('loggingInput');
    if (loggingInput) {
        loggingInput.value = lang === 'tr' ? 'EVET' : 'YES';
        console.log('📝 Logging input set to:', loggingInput.value);
    } else {
        console.warn('⚠️ loggingInput not found');
    }
}

function closeModal() {
    const modal = document.getElementById('finishModal');
    modal.classList.remove('show');
    modal.classList.add('hide');
    setTimeout(() => {
        modal.style.display = 'none';
        modal.classList.remove('hide');
    }, 300);
}

async function submitTaskDetails() {
    const detailText = document.getElementById('taskDetailInput').value.trim();
    if (!detailText) {
        showToast('⚠️ Please enter details!', 'error');
        return;
    }

    const end_time_unix = Math.floor(Date.now() / 1000);

    let meetings = [];
    if (currentMode === 'meeting') {
        meetings.push({ duration_seconds: totalSeconds, notes: detailText });
    }

    try {
        closeModal();
        resetTimer();
        showToast('💾 Saving details...', 'info');

        if (currentMode === 'work') {
            // Çalışma modunda normal task kaydı
            const saveRes = await fetch('/end_task_session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: user.email,
                    staff_id: String(user.staffid),
                    task_id: currentTaskId,
                    end_time: end_time_unix,
                    note: detailText
                })
            });

            if (saveRes.ok) {
                showToast('✅ Details saved!');
            } else {
                const saveJson = await saveRes.json();
                showToast('❌ Failed to save details', 'error');
                console.error('Save error:', saveJson);
            }
        }

        // Her iki modda da timesheet ve meeting bilgilerini gönder
        await sendTimesheetToBackend(meetings);
        // Çalışma moduna geçildiğinde başlat tuşunu her zaman enable et
        const startBtn = document.getElementById('startBtn');
        if (startBtn) {
            startBtn.disabled = false;
            startBtn.style.backgroundColor = 'green';
        }
    } catch (error) {
        console.error('❌ Error in submitTaskDetails:', error);
        showToast('❌ Error saving details', 'error');
        hideLoader();
    }
}

async function sendTimesheetToBackend(meetings = []) {
    const payload = [
        {
            task_id: currentMode === 'meeting' ? 'meeting' : document.getElementById('task').value,
            start_time: "10:00:00",
            end_time: "12:00:00",
            staff_id: String(user.staffid),
            hourly_rate: "5.00",
            note: document.getElementById('taskDetailInput').value.trim(),
            meetings: meetings.length > 0 ? meetings : undefined,
            email: user.email // Add email to payload
        }
    ];
    try {
        const res = await fetch('/insert_user_timesheet', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        console.log("✅ Timesheet sent:", result);
        showToast("✅ Timesheet sent!");

        // Send email after timesheet submission
        await fetch('/send_timesheet_email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: user.email, timesheet: payload[0] })
        });
        console.log("📧 Email sent for timesheet.");
    } catch (error) {
        console.error("❌ Error sending timesheet or email:", error);
    }
}

async function sendMeetingToLogoutTime(meetings = []) {
    try {
        const payload = {
            email: user.email,
            staff_id: String(user.staffid),
            total_duration: formatTime(totalSeconds),
            total_seconds: totalSeconds,
            meetings: meetings
        };

        const res = await fetch('/api/store_logout_time', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await res.json();
        console.log("✅ Meeting sent to logout time:", result);
    } catch (error) {
        console.error("❌ Error sending meeting to logout time:", error);
    }
}

function formatTime(seconds) {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs}h ${mins}m ${secs}s`;
}

function syncAllUsers() {
    fetch('/submit_all_data_files', {
        method: 'POST'
    })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            showToast(data.message || 'Synced successfully');
        })
        .catch(err => {
            console.error(err);
        });
}

function showLoader() {
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';
    const messages = {
        en: '🔄 Syncing timesheets...Please wait',
        tr: '🔄 Zaman çizelgeleri senkronize ediliyor... Lütfen bekleyin'
    };
    document.getElementById('syncLoader').innerHTML = `
<div style="padding: 20px; background: white; border-radius: 8px; font-weight: bold;">
${messages[lang]}
</div>
`;
    document.getElementById('syncLoader').style.display = 'flex';
}

function hideLoader() {
    document.getElementById('syncLoader').style.display = 'none';
}

window.addEventListener('DOMContentLoaded', () => {
    const animationBox = document.getElementById('work-animation');
    if (animationBox) {
        const gifImg = animationBox.querySelector('img');
        const gifs = [
            "https://media.tenor.com/bnYAs3wmjdYAAAAM/keyboard-type.gif",
            "https://i.gifer.com/embedded/download/11gv.gif",
            "https://www.icegif.com/wp-content/uploads/icegif-1850.gif",
            "https://www.icegif.com/wp-content/uploads/icegif-1852.gif",
            "https://gifdb.com/images/high/jabril-typing-with-toes-y859gmgutpzs3aqj.webp",
            "https://i.gifer.com/embedded/download/Cdm.gif",
            "https://i.gifer.com/embedded/download/So5.gif",
            "https://i.gifer.com/embedded/download/3XJG.gif",
            "https://i.gifer.com/embedded/download/3ev.gif",
            "https://i.gifer.com/embedded/download/Dx.gif",
            "https://i.gifer.com/embedded/download/2IN3.gif"
        ];

        const randomGif = gifs[Math.floor(Math.random() * gifs.length)];
        gifImg.src = randomGif;

        animationBox.classList.add('show');
        animationBox.style.display = 'block';

        setTimeout(() => {
            animationBox.classList.remove('show');
            setTimeout(() => {
                animationBox.style.display = 'none';
            }, 1000);
        }, 20000);
    }
});

function applyClientLanguage(lang) {
    const t = translations[lang];
    
    // State circle ve label
    const stateCircle = document.getElementById("stateCircle");
    let currentState = "work";
    if (stateCircle.classList.contains("idle")) currentState = "idle";
    else if (stateCircle.classList.contains("break")) currentState = "break";
    else if (stateCircle.classList.contains("meeting")) currentState = "meeting";

    document.getElementById("stateLabel").textContent = translations[lang][currentState] || currentState.toUpperCase();

    // Timer labels
    document.querySelectorAll(".timer-label")[0].textContent = t.hrs;
    document.querySelectorAll(".timer-label")[1].textContent = t.min;
    document.querySelectorAll(".timer-label")[2].textContent = t.sec;

    // Buttons
    document.getElementById("startBtn").textContent = t.start;
    document.getElementById("resetBtn").textContent = t.finish;

    // Mode selection buttons
    document.getElementById("workModeBtn").textContent = t.workMode;
    document.getElementById("meetingModeBtn").textContent = t.meetingMode;

    // Modal texts
    const idleModalTitle = document.getElementById("idleModalTitle");
    if (idleModalTitle) idleModalTitle.textContent = t.idleTitle;

    const idleModalDesc = document.getElementById("idleModalDesc");
    if (idleModalDesc) idleModalDesc.textContent = t.idleDesc;

    // Labels
    const labelMap = {
        client: t.client,
        totalLogged: t.totalLogged,
        totalTask: t.total,
        screenRecording: t.screenRecording,
        screenshotInterval: t.screenshotInterval
    };
    
    document.querySelectorAll('label[data-translatable]').forEach(label => {
        const key = label.getAttribute('data-translatable');
        if (labelMap[key]) label.textContent = labelMap[key];
    });

    // Dropdown placeholders
    const projectDropdown = document.getElementById("project");
    if (projectDropdown && projectDropdown.options.length > 0) {
        projectDropdown.options[0].textContent = t.selectProject;
    }

    const taskDropdown = document.getElementById("task");
    if (taskDropdown && taskDropdown.options.length > 0) {
        taskDropdown.options[0].textContent = t.selectTask;
    }

    // Modal translations
    document.getElementById('modalTitle').textContent = t.modalTitle;
    document.getElementById('modalDesc').textContent = t.modalDesc;
    document.getElementById('modalSubmitBtn').textContent = t.submit;
    document.getElementById('taskDetailInput').placeholder = t.modalPlaceholder;
    
    // Logout modal
    document.getElementById("logout").textContent = t.logout;
    if (document.getElementById("logoutModalTitle"))
        document.getElementById("logoutModalTitle").textContent = t.logoutTitle;
    if (document.getElementById("logoutModalDesc"))
        document.getElementById("logoutModalDesc").textContent = t.logoutDesc;
    if (document.getElementById("logoutConfirmBtn"))
        document.getElementById("logoutConfirmBtn").textContent = t.logoutConfirm;
    if (document.getElementById("logoutCancelBtn"))
        document.getElementById("logoutCancelBtn").textContent = t.logoutCancel;

    // Review modal
    const reviewModalTitle = document.getElementById("reviewModalTitle");
    if (reviewModalTitle) reviewModalTitle.textContent = t.feedbackTitle;
    const reviewModalDesc = document.getElementById("reviewModalDesc");
    if (reviewModalDesc) reviewModalDesc.textContent = t.feedbackDesc;
    const reviewInput = document.getElementById("reviewInput");
    if (reviewInput) reviewInput.placeholder = t.feedbackPlaceholder;
    const reviewSubmitBtn = document.getElementById("reviewSubmitBtn");
    if (reviewSubmitBtn) reviewSubmitBtn.textContent = t.feedbackSubmit;

    // Navigation
    if (document.getElementById("navDashboard"))
        document.getElementById("navDashboard").textContent = t.navDashboard;
    if (document.getElementById("navHelp"))
        document.getElementById("navHelp").textContent = t.navHelp;
    if (document.getElementById("navSettings"))
        document.getElementById("navSettings").textContent = t.navSettings;
    if (document.getElementById("navFeedback"))
        document.getElementById("navFeedback").textContent = t.navFeedback;

    // Remember me
    if (document.getElementById("rememberMeLabel")) {
        document.getElementById("rememberMeLabel").textContent = t.rememberMe;
    }

    // Logging input
    const loggingInput = document.getElementById('loggingInput');
    if (loggingInput) {
        const currentVal = loggingInput.value.toUpperCase();
        if (currentVal === 'YES' || currentVal === 'EVET') {
            loggingInput.value = lang === 'tr' ? 'EVET' : 'YES';
        } else if (currentVal === 'NO' || currentVal === 'HAYIR') {
            loggingInput.value = lang === 'tr' ? 'HAYIR' : 'NO';
        }
    }
}

window.addEventListener("load", () => {
    if (isTimerRunning) {
        console.log("🛑 App loaded: Auto-stopping timer");
        resetTimer();
        stopScreenRecording();
        stopDailyLogsCapture();
    }
});

window.addEventListener("beforeunload", async (event) => {
    if (isTimerRunning) {
        console.log("❌ App closing: Auto-stopping timer & saving session");

        const detailText = "Auto-saved due to app exit.";
        const end_time_unix = Math.floor(Date.now() / 1000);

        try {
            if (currentMode === 'work') {
                await fetch('/end_task_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: user.email,
                        staff_id: String(user.staffid),
                        task_id: currentTaskId,
                        end_time: end_time_unix,
                        note: detailText
                    })
                });
            } else {
                // Meeting modunda ise meeting bilgilerini gönder
                const meetings = [{ duration_seconds: totalSeconds, notes: detailText }];
                await sendMeetingToLogoutTime(meetings);
            }
        } catch (err) {
            console.error("❌ Failed to save task before exit:", err);
        }

        resetTimer();
        stopScreenRecording();
        stopDailyLogsCapture();
    }
});

async function uploadUsageLogToS3() {
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';
    let taskName = '';
    
    if (currentMode === 'work') {
        const taskSelect = document.getElementById('task');
        taskName = taskSelect.options[taskSelect.selectedIndex]?.textContent;
    } else {
        taskName = 'Meeting Session';
    }

    if (!taskName || !user?.email) {
        showToast(lang === 'tr' ? "⚠️ Lütfen görev seçin!" : "⚠️ Please select a task!", "error");
        return;
    }

    try {
        const res = await fetch('/upload_log_to_s3', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: user.email,
                task_name: taskName
            })
        });

        const data = await res.json();
        if (data.success) {
            console.log("📤 AI Summary:", data.summary);
        } else {
            showToast("❌ Failed: " + data.message, 'error');
        }
    } catch (err) {
        console.error("❌ Error uploading usage log:", err);
        showToast("❌ Unexpected error during log upload", "error");
    }
}

const stateConfig = {
    work: {
        label: 'WORK',
        message: 'Currently in WORK mode - Stay focused and productive! 💪',
    },
    idle: {
        label: 'IDLE',
        message: 'Taking a moment to breathe - Ready when you are! 🌟',
    },
    break: {
        label: 'BREAK',
        message: 'Break time! Recharge and come back stronger ☕',
    },
    meeting: {
        label: 'MEETING',
        message: 'In a meeting - Collaborating and connecting! 👥',
    }
};

function setState(state) {
    const stateCircle = document.getElementById('stateCircle');
    const stateLabel = document.getElementById('stateLabel');
    const statusText = document.getElementById('statusText');
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';

    const config = stateConfig[state];

    if (!stateCircle || !stateLabel) {
        console.warn("⛔ Missing stateCircle or stateLabel in DOM");
        return;
    }

    stateCircle.className = 'state-circle';
    stateCircle.classList.add(state);

    const translatedLabel = translations?.[lang]?.[state] || config.label;
    stateLabel.textContent = translatedLabel;

    if (statusText) {
        const message = translations?.[lang]?.statusText?.[state] || config.message;
        statusText.textContent = message;
    }

    const startBtn = document.getElementById('startBtn');
    const breakBtn = document.getElementById('breakBtn');

    if (state === 'work') {
        startBtn.disabled = false;
        startBtn.style.backgroundColor = 'green';
        if (breakBtn) {
            breakBtn.disabled = false;
            breakBtn.style.backgroundColor = '#007bff';
        }
    } else if (state === 'break') {
        if (breakBtn) {
            breakBtn.disabled = true;
            breakBtn.style.backgroundColor = 'gray';
        }
        startBtn.disabled = false;
        startBtn.style.backgroundColor = 'green';
    } else {
        startBtn.disabled = false;
        if (breakBtn) breakBtn.disabled = false;
        startBtn.style.backgroundColor = 'green';
        if (breakBtn) breakBtn.style.backgroundColor = '#007bff';
    }

    stateCircle.style.transform = 'scale(0.95)';
    setTimeout(() => {
        stateCircle.style.transform = '';
    }, 100);
}


// HTML'e eklenmesi gereken mode selection butonları için CSS
const modeSelectionCSS = `
<style>
.mode-selection {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    justify-content: center;
}

.mode-btn {
    padding: 12px 24px;
    border: 2px solid #006039;
    background: white;
    color: #006039;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    transition: all 0.3s ease;
}

.mode-btn.active {
    background: #006039;
    color: white;
}

.mode-btn:hover:not(.active) {
    background: #f0f0f0;
}
</style>
`;

// CSS'i document head'e ekle
document.head.insertAdjacentHTML('beforeend', modeSelectionCSS);

console.log('✅ Enhanced client.js with meeting mode functionality loaded');
let demoInterval;
function startDemo() {
    const states = ['work', 'idle', 'break', 'meeting'];
    let currentIndex = 0;

    demoInterval = setInterval(() => {
        currentIndex = (currentIndex + 1) % states.length;
        setState(states[currentIndex]);
    }, 5000);
}

function stopDemo() {
    if (demoInterval) {
        clearInterval(demoInterval);
    }
}

function handleBreak() {
    pauseTimer();
    setState('break');

    const breakBtn = document.getElementById('breakBtn');
    breakBtn.disabled = true;
    breakBtn.style.backgroundColor = 'gray';
}

function createRipple(event) {
    const button = event.currentTarget;
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');

    button.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 600);
}

function handleNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const navItems = document.querySelectorAll('.nav-item');

    navLinks.forEach((link, index) => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            navItems.forEach(item => item.classList.remove('active'));
            navItems[index].classList.add('active');

            createRipple(e);

            const page = link.dataset.page;
            console.log(`Navigating to: ${page}`);

            link.style.animation = 'none';
            setTimeout(() => {
                link.style.animation = '';
            }, 100);
        });
    });
}

function addAdvancedHoverEffects() {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const navText = link.querySelector('.nav-text');
        if (navText && navText.id === 'navFeedback') {
            return;
        }

        link.addEventListener('mouseenter', () => {
            link.style.transform = 'translateY(-5px) scale(1.02)';
        });

        link.addEventListener('mouseleave', () => {
            if (!link.parentElement.classList.contains('active')) {
                link.style.transform = 'translateY(0) scale(1)';
            }
        });

        link.addEventListener('mousemove', (e) => {
            const rect = link.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;

            link.style.transform = `translateY(-5px) scale(1.02) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    handleNavigation();
    addAdvancedHoverEffects();
    
    const feedbackLink = document.querySelector('.nav-link:has(#navFeedback)') || 
                        document.getElementById('navFeedback')?.closest('.nav-link');
    if (feedbackLink) {
        feedbackLink.style.transform = 'none';
        feedbackLink.style.transition = 'none';
    }

    const drawerArrowBtn = document.getElementById('drawerArrowBtn');
    if (drawerArrowBtn) {
        drawerArrowBtn.style.backgroundColor = '';
        drawerArrowBtn.style.borderColor = '';
        drawerArrowBtn.style.borderRadius = '';
        console.log('🔄 Drawer arrow button colors reset to CSS defaults');
    }

    const drawerElements = [
        document.querySelector('.drawer'),
        document.querySelector('.drawer-header'),
        document.querySelector('.drawer-content'),
        ...document.querySelectorAll('.drawer-section'),
        ...document.querySelectorAll('.drawer-section-header'),
        ...document.querySelectorAll('.drawer-item'),
        ...document.querySelectorAll('.project-details'),
        ...document.querySelectorAll('.task-details'),
        ...document.querySelectorAll('.time-details')
    ];

    drawerElements.forEach(element => {
        if (element) {
            element.style.backgroundColor = '';
            element.style.background = '';
            element.style.color = '';
        }
    });
    console.log('🔄 Drawer content background colors reset to CSS defaults');

    if (drawerArrowBtn) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    const target = mutation.target;
                    
                    if (target.id === 'drawerArrowBtn') {
                        if (target.style.backgroundColor && target.style.backgroundColor !== '') {
                            target.style.backgroundColor = '';
                        }
                        if (target.style.borderColor && target.style.borderColor !== '') {
                            target.style.borderColor = '';
                        }
                        console.log('🛡️ Prevented color override on drawer arrow button');
                    }
                    
                    if (target.classList.contains('drawer') ||
                        target.classList.contains('drawer-header') || 
                        target.classList.contains('drawer-content') ||
                        target.classList.contains('drawer-section') ||
                        target.classList.contains('drawer-section-header') ||
                        target.classList.contains('drawer-item') ||
                        target.classList.contains('project-details') ||
                        target.classList.contains('task-details') ||
                        target.classList.contains('time-details')) {
                        
                        if (target.style.backgroundColor && target.style.backgroundColor !== '') {
                            target.style.backgroundColor = '';
                        }
                        if (target.style.background && target.style.background !== '') {
                            target.style.background = '';
                        }
                        if (target.style.color && target.style.color !== '') {
                            target.style.color = '';
                        }
                        console.log('🛡️ Prevented color override on drawer element:', target.className);
                    }
                }
            });
        });
        
        observer.observe(drawerArrowBtn, { 
            attributes: true, 
            attributeFilter: ['style'] 
        });
        
        const allDrawerElements = [
            document.querySelector('.drawer'),
            document.querySelector('.drawer-header'),
            document.querySelector('.drawer-content'),
            ...document.querySelectorAll('.drawer-section'),
            ...document.querySelectorAll('.drawer-section-header'),
            ...document.querySelectorAll('.drawer-item'),
            ...document.querySelectorAll('.project-details'),
            ...document.querySelectorAll('.task-details'),
            ...document.querySelectorAll('.time-details')
        ];
        
        allDrawerElements.forEach(element => {
            if (element) {
                observer.observe(element, { 
                    attributes: true, 
                    attributeFilter: ['style'] 
                });
            }
        });
        
        console.log('🛡️ Protection set up for all drawer elements');
    }

    const container = document.querySelector('.nav-container');
    setTimeout(() => {
        container.style.transform = 'scale(1)';
        container.style.opacity = '1';
    }, 100);
});

document.addEventListener('keydown', (e) => {
    const activeItem = document.querySelector('.nav-item.active');
    const navItems = Array.from(document.querySelectorAll('.nav-item'));
    const currentIndex = navItems.indexOf(activeItem);

    if (e.key === 'ArrowLeft' && currentIndex > 0) {
        navItems[currentIndex].classList.remove('active');
        navItems[currentIndex - 1].classList.add('active');
        navItems[currentIndex - 1].querySelector('.nav-link').focus();
    } else if (e.key === 'ArrowRight' && currentIndex < navItems.length - 1) {
        navItems[currentIndex].classList.remove('active');
        navItems[currentIndex + 1].classList.add('active');
        navItems[currentIndex + 1].querySelector('.nav-link').focus();
    }
});

function openModalWithAnimation(modalId, callback) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    modal.style.display = "flex";
    setTimeout(() => {
      modal.classList.remove('hide');
      modal.classList.add('show');
      if (callback) callback();
    }, 10);
}

function closeModalWithAnimation(modalId, callback) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    modal.classList.remove('show');
    modal.classList.add('hide');
    
    setTimeout(() => {
      modal.style.display = "none";
      modal.classList.remove('hide');
      if (callback) callback();
    }, 300);
}

function openReviewModal() {
    const modal = document.getElementById("reviewModal");
    modal.style.display = "flex";
    setTimeout(() => {
      modal.classList.remove('hide');
      modal.classList.add('show');
    }, 10);
}

function closeReviewModal() {
    const modal = document.getElementById("reviewModal");
    modal.classList.remove('show');
    modal.classList.add('hide');
    
    setTimeout(() => {
      modal.style.display = "none";
      modal.classList.remove('hide');
    }, 300);
}

function submitUserReview() {
    const reviewText = document.getElementById('reviewInput').value.trim();
    const user = JSON.parse(sessionStorage.getItem('user'));

    if (!reviewText || !user?.email || !user?.firstName) {
        showToast('❗ Missing review or user info.', 'error');
        return;
    }

    fetch('/submit-feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email: user.email,
            username: `${user.firstName} ${user.lastName || ''}`.trim(),
            message: reviewText
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            showToast('✅ Feedback sent successfully!');
            closeReviewModal();
            document.getElementById('reviewInput').value = '';
        } else {
        }
    })
    .catch(err => {
        console.error('Feedback error:', err);
        showToast('❌ Feedback error occurred.', 'error');
    });
}

function openInNewTab(url) {
    try {
        window.open(url, '_blank');
    } catch (err) {
        console.error("❌ Failed to open new tab:", err);
    }
}

function openLogoutModal() {
  if (isTimerRunning) {
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';
    const warning = lang === 'tr'
      ? "⛔ Zamanlayıcı çalışırken çıkış yapamazsınız. Lütfen önce görevi bitirin."
      : "⛔ You cannot logout while the timer is running. Please finish your task first.";

    showToast(warning, "error");
    return;
  }

  const modal = document.getElementById("logoutModal");
  modal.style.display = "flex";
  setTimeout(() => {
    modal.classList.remove('hide');
    modal.classList.add('show');
  }, 10);
}

function closeLogoutModal() {
    const modal = document.getElementById("logoutModal");
    modal.classList.remove('show');
    modal.classList.add('hide');
    
    setTimeout(() => {
      modal.style.display = "none";
      modal.classList.remove('hide');
    }, 300);
}

function closeIdleModal() {
}

function cancelIdleCountdown() {
    clearInterval(idleCountdownInterval);
    closeIdleModal();

    sessionStartTime = Math.floor(Date.now() / 1000);

    startTimer();
    setState('work');
    showToast("⏱️ Countdown canceled. Back to work!", "success");
}

setInterval(() => {
    console.log('🔄 Client.js: Periodic styling refresh...');
}, 5 * 60 * 1000);

window.refreshStyling = function() {
    console.log('🧪 Manual styling refresh triggered...');
};

window.testClientStyling = function() {
    console.log('🧪 Testing client styling integration...');
    
    const buttonSelectors = ['#startBtn', '#resetBtn', '.modal-btn', 'button'];
    buttonSelectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        console.log(`🔍 Found ${elements.length} elements for selector: ${selector}`);
    });
};

window.debugClientColors = function() {
    const root = document.documentElement;
    const style = getComputedStyle(root);
    
    console.log('🎨 Current Client.js CSS Variables:');
    console.log('--primary-color:', style.getPropertyValue('--primary-color').trim());
    console.log('--secondary-color:', style.getPropertyValue('--secondary-color').trim());
    console.log('--background-color:', style.getPropertyValue('--background-color').trim());
    console.log('--button-color:', style.getPropertyValue('--button-color').trim());
    console.log('--text-color:', style.getPropertyValue('--text-color').trim());
    
    console.log('🎯 NEW Color Fields:');
    console.log('--header-color:', style.getPropertyValue('--header-color').trim());
    console.log('--footer-color:', style.getPropertyValue('--footer-color').trim());
    console.log('--button-text-color:', style.getPropertyValue('--button-text-color').trim());
    
    const startBtn = document.getElementById('startBtn');
    if (startBtn) {
        const btnStyle = getComputedStyle(startBtn);
        console.log('🔴 Start Button Background:', btnStyle.backgroundColor);
        console.log('🔴 Start Button Color (text):', btnStyle.color);
        console.log('🔴 Start Button Border:', btnStyle.borderColor);
    }

    const logoutBtn = document.getElementById('logout');
    if (logoutBtn) {
        const logoutStyle = getComputedStyle(logoutBtn);
        console.log('🔒 Logout Button Background:', logoutStyle.backgroundColor);
        console.log('🔒 Logout Button Color:', logoutStyle.color);
        console.log('🔒 Logout Button Border:', logoutStyle.borderColor);
    }

    const languageBtn = document.querySelector('.language-btn');
    if (languageBtn) {
        const langStyle = getComputedStyle(languageBtn);
        console.log('🌐 Language Button Background:', langStyle.backgroundColor);
        console.log('🌐 Language Button Color:', langStyle.color);
        console.log('🌐 Language Button Border:', langStyle.borderColor);
    }

    const headerElements = document.querySelectorAll('header, .header, .window-header');
    headerElements.forEach((header, index) => {
        const headerStyle = getComputedStyle(header);
        console.log(`🎯 Header ${index + 1} Background:`, headerStyle.backgroundColor);
    });

    const footerElements = document.querySelectorAll('footer, .footer');
    footerElements.forEach((footer, index) => {
        const footerStyle = getComputedStyle(footer);
        console.log(`🎯 Footer ${index + 1} Background:`, footerStyle.backgroundColor);
    });
};

const originalSetState = setState;
setState = function(state) {
    originalSetState(state);
    
    setTimeout(() => {
    }, 100);
};

console.log('✅ Client.js: DDS Styling API integration completed');
console.log('🧪 Debug functions available: refreshStyling(), testClientStyling(), debugClientColors()');

window.testAllAPIColorFields = async function() {
    console.log('🧪 Testing ALL API Color Fields...');
    
    try {
        const root = document.documentElement;
        const style = getComputedStyle(root);
        
        console.log('🎨 Current CSS Variables:');
        console.log('=======================================');
        console.log('--header-color:', style.getPropertyValue('--header-color').trim());
        console.log('--footer-color:', style.getPropertyValue('--footer-color').trim());
        console.log('--button-text-color:', style.getPropertyValue('--button-text-color').trim());
        console.log('--text-color:', style.getPropertyValue('--text-color').trim());
        console.log('--background-color:', style.getPropertyValue('--background-color').trim());
        console.log('--button-color:', style.getPropertyValue('--button-color').trim());
        
        console.log('✅ API Color Fields Test Complete!');
        return true;
    } catch (error) {
        console.error('❌ API Color Fields Test Error:', error);
        return false;
    }
};

console.log('🆕 New function available: testAllAPIColorFields()');

window.verifyColorImplementation = function() {
    console.log('🔍 Verifying Color Field Implementation...');
    
    const colorTests = [
        {
            name: 'Header Elements',
            selectors: ['header', '.header', '.window-header', '.navbar'],
            property: 'background-color',
            expectedVar: '--header-color'
        },
        {
            name: 'Footer Elements', 
            selectors: ['footer', '.footer', '.bottom-footer'],
            property: 'background-color',
            expectedVar: '--footer-color'
        },
        {
            name: 'Button Text',
            selectors: ['button:not(#logout):not(.language-btn)', '.btn:not(#logout):not(.language-btn)'],
            property: 'color',
            expectedVar: '--button-text-color'
        }
    ];
    
    colorTests.forEach(test => {
        console.log(`\n🧪 Testing ${test.name}:`);
        test.selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            console.log(`  ${selector}: Found ${elements.length} elements`);
            
            elements.forEach((element, index) => {
                const style = getComputedStyle(element);
                const value = style.getPropertyValue(test.property);
                console.log(`    Element ${index + 1}: ${test.property} = ${value}`);
            });
        });
    });
    
    console.log('\n✅ Color Implementation Verification Complete!');
};

console.log('🆕 New function available: verifyColorImplementation()');

window.forceWhiteHeaderButtons = function() {
    console.log('🔒 Forcing white header button styling...');
    
    const logoutBtn = document.getElementById('logout');
    if (logoutBtn) {
        logoutBtn.style.setProperty('background-color', 'white', 'important');
        logoutBtn.style.setProperty('color', 'white', 'important');
        logoutBtn.style.setProperty('border-color', 'white', 'important');
        console.log('✅ Logout button forced to white');
    }

    const languageBtn = document.querySelector('.language-btn');
    if (languageBtn) {
        languageBtn.style.setProperty('background-color', 'white', 'important');
        languageBtn.style.setProperty('color', 'white', 'important');
        languageBtn.style.setProperty('border-color', 'white', 'important');
        console.log('✅ Language button forced to white');
    }

    console.log('🔒 White header button styling complete');
};

console.log('🔒 Additional function: forceWhiteHeaderButtons()');

function preventNavigationBlackBackgrounds() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    const style = link.getAttribute('style');
                    if (style && (style.includes('rgb(0, 0, 0)') || style.includes('background-color: black') || style.includes('background: black'))) {
                        const cleanStyle = style
                            .replace(/background-color:\s*rgb\(0,\s*0,\s*0\)\s*!important;?/gi, '')
                            .replace(/background-color:\s*black\s*!important;?/gi, '')
                            .replace(/background:\s*rgb\(0,\s*0,\s*0\)\s*!important;?/gi, '')
                            .replace(/background:\s*black\s*!important;?/gi, '');
                        
                        link.setAttribute('style', cleanStyle);
                        console.log('🛡️ Prevented black background on navigation link');
                    }
                }
            });
        });
        
        observer.observe(link, { attributes: true, attributeFilter: ['style'] });
    });
}

document.addEventListener('DOMContentLoaded', preventNavigationBlackBackgrounds);

// End of client.js