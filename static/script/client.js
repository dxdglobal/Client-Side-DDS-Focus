let isStartInProgress = false;
let isSubmitInProgress = false;
let isResetInProgress = false;
let idleTriggerTime = 0;
let idleTimeout = 5;  // modal stays 5 seconds before sending auto-note


const translations = {
    en: {
        welcome: "Welcome...",
        logging: "Logging",
        total: "Total Time Count",
        loadingTasks: "Loading tasks...",
        idleTitle: "⏸️ You're Idle",
        idleDesc: "You’ve been inactive. Timer is paused.",
        min: "min",
        today: "Today",
        work: "WORK",
        start: "START",
        finish: "Finish",
        hrs: "HRS",
        min: "MIN",
        sec: "SEC",
        modalTitle: "📝 Task Completion",
        modalDesc: "Please describe what you have completed for this task:",
        submit: "Submit",
        selectTask: "-- Select a Task --",
        loadingProjects: "Loading projects...",
        user: "User",
        project: "Project",
        task: "Task",
        client: "Client",
        modalTitle: "📝 Task Completion",
        modalDesc: "Please describe what you have completed for this task:",
        modalPlaceholder: "Type your task details here...",
        submit: "Submit",
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
        rememberMe: "Remember Me"
    },
    tr: {
        welcome: "Hoş geldin...",
        logging: "Ekran Kaydı",
        total: "Toplam Süre",
        minWorkWarning: "⚠️ Bir görevi bitirmek için en az 1 dakika çalışmalısınız.",
        idle: "BOŞTA",
        break: "MOLA",
        min: "dk", // or "dakika" if preferred
        meeting: "TOPLANTI",
        today: "Tarih",
        work: "ÇALIŞMA",
        loadingTasks: "Görevler yükleniyor...",
        idleTitle: "⏸️ Boştasınız",
        idleDesc: "Bir süredir işlem yapılmadı. Sayaç duraklatıldı.",
        start: "BAŞLAT",
        finish: "Bitir",
        hrs: "SA",
        min: "DK",
        sec: "SN",
        modalTitle: "📝 İş Tamamlandı",
        modalDesc: "Bu İş Emri için ne yaptığınızı açıklayın:",
        submit: "Gönder",
        selectTask: "-- İş Emri Seçin --",
        loadingProjects: "Projeler yükleniyor...",
        user: "Kullanıcı",
        project: "Proje",
        task: "İş Emri",
        client: "Personel",
        modalTitle: "📝 İş Emri Tamamlandı",
        modalDesc: "Bu iş emri için ne yaptığınızı açıklayın:",
        modalPlaceholder: "İş Emri detaylarını buraya yazın...",
        submit: "Gönder",
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
        rememberMe: "Beni Hatırla"
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

            function updateDrawerContent(projectName, taskName) {
                // Update project details
                const drawerProjectName = document.getElementById('drawerProjectName');
                const drawerProjectDesc = document.getElementById('drawerProjectDesc');
                
                if (drawerProjectName) {
                    drawerProjectName.textContent = projectName || 'No Project Selected';
                }
                if (drawerProjectDesc) {
                    drawerProjectDesc.textContent = `Working on: ${projectName || 'No project selected'}`;
                }
                
                // Update task details
                const drawerTaskName = document.getElementById('drawerTaskName');
                const drawerTaskDesc = document.getElementById('drawerTaskDesc');
                
                if (drawerTaskName) {
                    drawerTaskName.textContent = taskName || 'No Task Selected';
                }
                if (drawerTaskDesc) {
                    drawerTaskDesc.textContent = `Current task: ${taskName || 'No task selected'}`;
                }
                
                // Update session info
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
        // document.getElementById('profileImage').src = `https://crm.deluxebilisim.com/uploads/staff_profile_images/${user.staffid}/small_${user.profileImage}`;
        const profileImg = document.getElementById('profileImage');
        const imgUrl = `https://crm.deluxebilisim.com/uploads/staff_profile_images/${user.staffid}/small_${user.profileImage}`;
        profileImg.src = imgUrl;
        profileImg.onerror = function () {
            this.onerror = null; // prevent infinite loop
            this.src = "../static/images/user_placeholder.png"; // Local fallback
        };

        fetchAIProjects(user);
        saveUserProjectsToCache(user);
    }






let idleCountdownInterval;

setInterval(() => {
    if (!isTimerRunning) return;

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





                   idleModal.style.display = 'flex';

                    const idleContent = idleModal.querySelector(".modal-content");
                    idleContent.classList.remove('idle-shake');
                    void idleContent.offsetWidth;
                    idleContent.classList.add('idle-shake');

                    // ⏱️ Directly call auto submit without countdown
                    setTimeout(() => {
                        handleAutoIdleSubmit();
                    }, 5000);  // Keep 5s visual delay if needed








                }
            }
        })
        .catch(console.error);
}, 10000);




    };
    
async function handleAutoIdleSubmit() {
    stopScreenRecording();  // ✅ Yeh yahan hona chahiye, function ke andar nahi
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';

    // ✅ Total idle = 5 minutes (300s) + modal display (5s)
    const totalIdleSeconds = 180;

    const actualEndTime = Math.floor(idleTriggerTime / 1000);
    const adjustedEndTime = actualEndTime - totalIdleSeconds;
    const durationWorked = adjustedEndTime - sessionStartTime;

    const minsWorked = durationWorked >= 60 ? Math.floor(durationWorked / 60) : 0;
    const idleMsg = lang === 'tr'
    ? (minsWorked === 0
        ? `Kullanıcı 1 dakikadan az çalıştı ve ${totalIdleSeconds} saniye boşta kaldı.`
        : `Kullanıcı ${minsWorked} dakika çalıştı ve ${totalIdleSeconds} saniye boşta kaldı.`)
    : (minsWorked === 0
        ? `User worked for less than 1 minute and stayed idle for ${totalIdleSeconds} seconds.`
        : `User worked for ${minsWorked} minutes and stayed idle for ${totalIdleSeconds} seconds.`);


    // 👇 ADD THIS LINE
const secsWorked = durationWorked % 60;
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
        stopDailyLogsCapture(); // ✅ Stop daily logs capture
        showToast('✅ Auto-saved due to idle', 'success');
    } catch (error) {
        console.error("❌ Failed to auto-save:", error);
        // showToast("❌ Auto-save failed", "error");
    }
}



document.getElementById('startBtn').addEventListener('click', function () {
    const taskSelect = document.getElementById('task');
    const selectedTaskOption = taskSelect.options[taskSelect.selectedIndex];
    const taskId = taskSelect.value;

    if (!taskId || taskId === "" || selectedTaskOption.disabled) {
        showToast('⚠️ Please select a task first!', 'error');
        return;
    }

    if (!isTimerRunning) {
        currentTaskId = taskId;
        sessionStartTime = Math.floor(Date.now() / 1000);  // ✅ UNIX timestamp

        selectedProjectName = document.getElementById('project').selectedOptions[0]?.textContent || '';
        selectedTaskName = selectedTaskOption.textContent;

        // Update drawer content with selected project and task
        updateDrawerContent(selectedProjectName, selectedTaskName);

        fetch('/start_screen_recording', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: user.email,
                project: selectedProjectName,
                task: selectedTaskName
            })
        }).catch(console.error);

        // ✅ Start automatic daily logs capture
        startDailyLogsCapture();

        startTimer();

        // ✅ Automatically update stateCircle to WORK
        setState('work');
    }
});







document.getElementById('resetBtn').addEventListener('click', () => {
    if (totalSeconds < 10) {
        // resetTimer();
        // stopScreenRecording();
        const lang = sessionStorage.getItem('selectedLanguage') || 'en';
        const message = translations[lang].minWorkWarning;
        showToast(message, 'error');
        return;
    }
    openModal();
});

// let sessionStartTime;
function startTimer() {
    // clearInterval(timerInterval);
    sessionStartTime = Math.floor(Date.now() / 1000);
    const unixStart = Math.floor(sessionStartTime / 1000);
    // console.log("⏱️ Session Start Timestamp:", sessionStartTime);



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
            start_time: sessionStartTime  // 🔥 Already a number


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






    isTimerRunning = true;
    document.getElementById('startBtn').disabled = true;

    document.getElementById('startBtn').style.backgroundColor = 'gray';
    document.getElementById('project').disabled = true;
    document.getElementById('task').disabled = true;
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

    // Reset display
    document.getElementById('hours').innerText = '00';
    document.getElementById('minutes').innerText = '00';
    document.getElementById('seconds').innerText = '00';

    // ✅ Reactivate the Start button
    document.getElementById('startBtn').disabled = false;
    document.getElementById('startBtn').style.backgroundColor = 'green';

    // Enable dropdowns again
    const projectSelect = document.getElementById('project');
    const taskSelect = document.getElementById('task');
    projectSelect.disabled = false;
    taskSelect.disabled = false;

    // Reset dropdowns
    projectSelect.selectedIndex = 0;
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';
    const taskPlaceholder = lang === 'tr' ? '-- İş Emri Seçin --' : '-- Select a Task --';
    taskSelect.innerHTML = `<option disabled selected>${taskPlaceholder}</option>`;

    // Logging input reset
    document.getElementById('loggingInput').value = lang === 'tr' ? 'HAYIR' : 'NO';
    document.getElementById('totaltimecount').innerText = `0 min 0 sec`;
}


function updateTimerDisplay() {
    totalSeconds++;

    document.getElementById('hours').innerText = String(Math.floor(totalSeconds / 3600)).padStart(2, '0');
    document.getElementById('minutes').innerText = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0');
    document.getElementById('seconds').innerText = String(totalSeconds % 60).padStart(2, '0');

    // ✅ Live update Total Time Count with translation
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';

    const labelMin = translations[lang].min || 'min';
    const labelSec = translations[lang].sec || 'sec';  // 👈 make sure `sec` exists in translations

    document.getElementById('totaltimecount').innerText = `${mins} ${labelMin} ${secs} ${labelSec}`;
}


function stopScreenRecording() {
    fetch('/stop_screen_recording', { method: 'POST' })
        .then(res => res.json())
        // .then(data => console.log("🛑 Recording stopped:", data))
        .catch(console.error);
        
}

// ✅ Daily logs capture functions
let dailyLogsInterval;

function startDailyLogsCapture() {
    console.log("📋 Starting automatic daily logs capture...");
    
    // Capture initial log when work starts
    captureCurrentActivityLog();
    
    // Set interval to capture logs every 60 seconds (1 minute)
    dailyLogsInterval = setInterval(() => {
        captureCurrentActivityLog();
    }, 60000); // 60 seconds
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
        activity_type: isTimerRunning ? 'working' : 'idle',
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

            // showToast(`✅ Found ${projects.length} projects`);
        })
        .catch(error => {
            console.error(error);
            showToast('❌ Error loading projects', 'error');
        });
}
function loadTasksForProject() {
    const projectId = document.getElementById('project').value;
    const taskSelect = document.getElementById('task');
    if (!projectId) {
        taskSelect.innerHTML = '<option disabled selected>-- Select a Task --</option>';
        return;
    }

    taskSelect.innerHTML = '<option disabled selected>Loading tasks...</option>';

    fetch(`/get_tasks/${projectId}`)  // or /get_active_tasks if you're using status=2 only
        .then(response => response.json())
        .then(data => {
            taskSelect.innerHTML = '';
            const placeholder = new Option('-- Select a Task --', '');
            placeholder.disabled = true;
            placeholder.selected = true;
            taskSelect.appendChild(placeholder);

            const tasks = data.tasks || [];
            tasks.forEach(task => {
                const option = new Option(task.name || task.subject || 'Unnamed Task', task.id);
                taskSelect.appendChild(option);
            });

            // ✅ Print task details in console
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
            // console.log("🕒 Task time summary:", data.summary);
        })
        .catch(err => console.error("❌ Error loading task times:", err));
}

function openModal() {
    // clearInterval(timerInterval); 
    document.getElementById('finishModal').style.display = 'flex';
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';
    document.getElementById('loggingInput').value = lang === 'tr' ? 'EVET' : 'YES';


}

function closeModal() {
    document.getElementById('finishModal').style.display = 'none';
}



async function submitTaskDetails() {
    const detailText = document.getElementById('taskDetailInput').value.trim();
    if (!detailText) {
        showToast('⚠️ Please enter task details!', 'error');
        return;
    }

    const end_time_unix = Math.floor(Date.now() / 1000); // UNIX format
    const taskId = document.getElementById('task').value;

    console.log("📤 Sending to /end_task_session:");
    console.log("📧 Email:", user.email);
    console.log("🆔 Task ID:", taskId);
    console.log("🕐 End Time (UNIX):", end_time_unix);
    console.log("📝 Note:", detailText);

    try {
        // ⚡ Close modal immediately for better UX
        closeModal();
        resetTimer();
        showToast('💾 Saving task details...', 'info');

        // First, send the critical task completion data
        const saveRes = await fetch('/end_task_session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: user.email,
                staff_id: String(user.staffid),
                task_id: taskId,
                end_time: end_time_unix,
                note: detailText
            })
        });

        if (saveRes.ok) {
            showToast('✅ Task details saved!');
            
            // ⚡ Send timesheet data first, then other operations in background
            await sendTimesheetToBackend();
            
            // Show loader for background operations
            showLoader();

            // ⚡ Run these operations in parallel instead of sequentially
            Promise.all([
                fetch('/submit_all_data_files', { method: 'POST' }).catch(err => console.warn('Data files error:', err)),
                fetch('/upload_screenshots', { method: 'POST' }).catch(err => console.warn('Screenshots error:', err)),
                uploadUsageLogToS3().catch(err => console.warn('S3 upload error:', err))
            ]).then(() => {
                hideLoader();
                console.log('✅ All background operations completed');
            }).catch(err => {
                console.warn('⚠️ Some background operations failed:', err);
                hideLoader();
            });
            
        } else {
            const saveJson = await saveRes.json();
            showToast('❌ Failed to save task details', 'error');
            console.error('Save error:', saveJson);
        }

    } catch (error) {
        console.error('❌ Error in submitTaskDetails:', error);
        showToast('❌ Error saving task details', 'error');
        hideLoader();
    }
}



async function sendTimesheetToBackend() {
    const payload = [
        {
            task_id: document.getElementById('task').value,
            start_time: "10:00:00", // 👈 yeh tum calculate ya assign kar sakte ho
            end_time: "12:00:00",   // 👈 current time use bhi kar sakte ho
            staff_id: String(user.staffid),
            hourly_rate: "5.00",
            note: document.getElementById('taskDetailInput').value.trim()
        }
    ];

    try {
        const res = await fetch('/insert_user_timesheet', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await res.json();
        console.log("✅ Server response:", result);
        showToast("✅ Timesheet sent!");
    } catch (error) {
        console.error("❌ Error sending timesheet:", error);
        // showToast("❌ Failed to send!", "error");
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
            // showToast('❌ Failed to sync all users', 'error');
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
});



function applyClientLanguage(lang) {




    const t = translations[lang];
    document.querySelector("#work-animation p").textContent = t.welcome;
    const stateCircle = document.getElementById("stateCircle");
    let currentState = "work";

    if (stateCircle.classList.contains("idle")) currentState = "idle";
    else if (stateCircle.classList.contains("break")) currentState = "break";
    else if (stateCircle.classList.contains("meeting")) currentState = "meeting";

    document.getElementById("stateLabel").textContent = translations[lang][currentState] || currentState.toUpperCase();


    document.querySelectorAll(".timer-label")[0].textContent = t.hrs;
    document.querySelectorAll(".timer-label")[1].textContent = t.min;
    document.querySelectorAll(".timer-label")[2].textContent = t.sec;

    // Update button text
    document.getElementById("startBtn").textContent = t.start;
    document.getElementById("resetBtn").textContent = t.finish;

    const idleModalTitle = document.getElementById("idleModalTitle");
    if (idleModalTitle) idleModalTitle.textContent = t.idleTitle;

    const idleModalDesc = document.getElementById("idleModalDesc");
    if (idleModalDesc) idleModalDesc.textContent = t.idleDesc;

    // Safely update labels
    const allLabels = document.querySelectorAll('label');
    allLabels.forEach(label => {
        const htmlFor = label.getAttribute('for');
        if (htmlFor === 'loggingInput') label.textContent = t.logging;
        if (htmlFor === 'totaltimecount') label.textContent = t.total;
        if (htmlFor === 'todayDate') label.textContent = t.today;
        if (htmlFor === "clientNameInput") label.textContent = t.client;
        if (htmlFor === "project") label.textContent = t.project;
        if (htmlFor === "task") label.textContent = t.task;
        if (htmlFor === "loggingInput") label.textContent = t.logging;
        if (htmlFor === "totaltimecount") label.textContent = t.total;
        if (htmlFor === "todayDate") label.textContent = t.today;
    });

    // Update dropdown placeholders
    const projectDropdown = document.getElementById("project");
    if (projectDropdown.options.length > 0) {
        projectDropdown.options[0].textContent = t.selectProject;
    }

    const taskDropdown = document.getElementById("task");
    if (taskDropdown.options.length > 0) {
        taskDropdown.options[0].textContent = t.selectTask;
    }

    // Modal translations
    document.getElementById('modalTitle').textContent = t.modalTitle;
    document.getElementById('modalDesc').textContent = t.modalDesc;
    document.getElementById('modalSubmitBtn').textContent = t.submit;
    document.getElementById('taskDetailInput').placeholder = t.modalPlaceholder;
    document.getElementById("logout").textContent = t.logout;

    if (document.getElementById("logoutModalTitle"))
    document.getElementById("logoutModalTitle").textContent = t.logoutTitle;

    if (document.getElementById("logoutModalDesc"))
    document.getElementById("logoutModalDesc").textContent = t.logoutDesc;

    if (document.getElementById("logoutConfirmBtn"))
    document.getElementById("logoutConfirmBtn").textContent = t.logoutConfirm;

    if (document.getElementById("logoutCancelBtn"))
    document.getElementById("logoutCancelBtn").textContent = t.logoutCancel;


    const reviewModalTitle = document.getElementById("reviewModalTitle");
    if (reviewModalTitle) reviewModalTitle.textContent = t.feedbackTitle;

    const reviewModalDesc = document.getElementById("reviewModalDesc");
    if (reviewModalDesc) reviewModalDesc.textContent = t.feedbackDesc;

    const reviewInput = document.getElementById("reviewInput");
    if (reviewInput) reviewInput.placeholder = t.feedbackPlaceholder;

    const reviewSubmitBtn = document.getElementById("reviewSubmitBtn");
    if (reviewSubmitBtn) reviewSubmitBtn.textContent = t.feedbackSubmit;


    if (document.getElementById("navDashboard"))
        document.getElementById("navDashboard").textContent = t.navDashboard;

        if (document.getElementById("navHelp"))
        document.getElementById("navHelp").textContent = t.navHelp;

        if (document.getElementById("navSettings"))
        document.getElementById("navSettings").textContent = t.navSettings;

        if (document.getElementById("navFeedback"))
        document.getElementById("navFeedback").textContent = t.navFeedback;

if (document.getElementById("rememberMeLabel")) {
document.getElementById("rememberMeLabel").textContent = t.rememberMe;
}

if (document.getElementById("logoutModalTitle")) {
document.getElementById("logoutModalTitle").textContent = t.logoutTitle;
}

if (document.getElementById("logoutModalDesc")) {
document.getElementById("logoutModalDesc").textContent = t.logoutDesc;
}

if (document.getElementById("logoutCancelBtn")) {
document.getElementById("logoutCancelBtn").textContent = t.logoutCancel;
}

if (document.getElementById("logoutConfirmBtn")) {
document.getElementById("logoutConfirmBtn").textContent = t.logoutConfirm;
}







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



// ✅ Inject into <script> block of client.html or external JS file
window.addEventListener("load", () => {
    if (isTimerRunning) {
        console.log("🛑 App loaded: Auto-stopping timer");
        resetTimer();
        stopScreenRecording();
        stopDailyLogsCapture(); // ✅ Stop daily logs capture
    }
});

window.addEventListener("beforeunload", async (event) => {
    if (isTimerRunning) {
        console.log("❌ App closing: Auto-stopping timer & saving session");

        const detailText = "Auto-saved due to app exit.";
        const end_time_unix = Math.floor(Date.now() / 1000);

        try {
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
        } catch (err) {
            console.error("❌ Failed to save task before exit:", err);
        }

        resetTimer();
        stopScreenRecording();
        stopDailyLogsCapture(); // ✅ Stop daily logs capture
    }
});



async function uploadUsageLogToS3() {
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';
    const taskSelect = document.getElementById('task');
    const taskName = taskSelect.options[taskSelect.selectedIndex]?.textContent;

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
            // showToast("✅ AI summary created and uploaded!");

            // OPTIONAL: Show inside alert/modal
            // alert(`🧠 AI Summary:\n\n${data.summary}`);

        } else {
            showToast("❌ Failed: " + data.message, 'error');
        }
    } catch (err) {
        console.error("❌ Error uploading usage log:", err);
        showToast("❌ Unexpected error during log upload", "error");
    }
}

       

const stateCircle = document.getElementById('stateCircle');
const stateLabel = document.getElementById('stateLabel');
const statusText = document.getElementById('statusText');
// const particlesContainer = document.getElementById('particles');

const stateConfig = {
    work: {
        label: 'WORK',
        message: 'Currently in WORK mode - Stay focused and productive! 💪',
        // particles: false
    },
    idle: {
        label: 'IDLE',
        message: 'Taking a moment to breathe - Ready when you are! 🌟',
        // particles: false
    },
    break: {
        label: 'BREAK',
        message: 'Break time! Recharge and come back stronger ☕',
        // particles: false
    },
    meeting: {
        label: 'MEETING',
        message: 'In a meeting - Collaborating and connecting! 👥',
        // particles: false
    }
};

function setState(state) {
    const stateCircle = document.getElementById('stateCircle');
    const stateLabel = document.getElementById('stateLabel');
    const statusText = document.getElementById('statusText');
    const lang = sessionStorage.getItem('selectedLanguage') || 'en';

    const config = stateConfig[state];

    // ✅ Safety check
    if (!stateCircle || !stateLabel) {
        console.warn("⛔ Missing stateCircle or stateLabel in DOM");
        return;
    }

    // ✅ Update visual class
    stateCircle.className = 'state-circle';
    stateCircle.classList.add(state);

    // ✅ State label: translated if available
    const translatedLabel = translations?.[lang]?.[state] || config.label;
    stateLabel.textContent = translatedLabel;

    // ✅ Status message: translated if available
    if (statusText) {
        const message = translations?.[lang]?.statusText?.[state] || config.message;
        statusText.textContent = message;
    }

    // ✅ Button handling
    const startBtn = document.getElementById('startBtn');
    const breakBtn = document.getElementById('breakBtn');

    if (state === 'work') {
        startBtn.disabled = true;
        startBtn.style.backgroundColor = 'gray';
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

    // ✅ Small animation pulse
    stateCircle.style.transform = 'scale(0.95)';
    setTimeout(() => {
        stateCircle.style.transform = '';
    }, 100);
}



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
    pauseTimer();        // ⏸️ Timer stop karo
    setState('break');   // ☕ Status circle break kar do

    // ✅ Immediately disable Break button
    const breakBtn = document.getElementById('breakBtn');
    breakBtn.disabled = true;
    breakBtn.style.backgroundColor = 'gray';
}

      
            // Ripple effect on click
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

            // Navigation functionality
function handleNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const navItems = document.querySelectorAll('.nav-item');

    navLinks.forEach((link, index) => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            // Remove active class from all items
            navItems.forEach(item => item.classList.remove('active'));

            // Add active class to clicked item
            navItems[index].classList.add('active');

            // Create ripple effect
            createRipple(e);

            // Simulate page change with a subtle animation
            const page = link.dataset.page;
            console.log(`Navigating to: ${page}`);

            // Add a slight shake animation to show interaction
            link.style.animation = 'none';
            setTimeout(() => {
                link.style.animation = '';
            }, 100);
        });
    });
}

            // Smooth hover effects with mousemove
function addAdvancedHoverEffects() {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
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

            // Initialize everything when page loads
document.addEventListener('DOMContentLoaded', () => {
    handleNavigation();
    // createParticles();
    addAdvancedHoverEffects();

    // Add a subtle entrance animation to the container
    const container = document.querySelector('.nav-container');
    setTimeout(() => {
        container.style.transform = 'scale(1)';
        container.style.opacity = '1';
    }, 100);
});

// Add keyboard navigation
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




// For Review Modal js  
// === REVIEW MODAL CONTROL ===
function openReviewModal() {
    document.getElementById("reviewModal").style.display = "flex";
}

function closeReviewModal() {
    document.getElementById("reviewModal").style.display = "none";
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
            // showToast('❌ Failed to send feedback: ' + data.message, 'error');
        }
    })
    .catch(err => {
        console.error('Feedback error:', err);
        showToast('❌ Feedback error occurred.', 'error');
    });
}


function openInNewTab(url) {
    try {
        // Works in browser or will call default system browser from PyWebview
        window.open(url, '_blank');
    } catch (err) {
        console.error("❌ Failed to open new tab:", err);
    }
}



function logout() {
  if (isTimerRunning) {
    showToast("⛔ You cannot logout while the timer is running. Please finish your task first.", "error");
    return;
  }

  if (confirm("Are you sure you want to logout?")) {
    sessionStorage.clear();
    window.location.href = '/';
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

  // ✅ Open modal if timer is NOT running
  document.getElementById("logoutModal").style.display = "flex";
}


function closeLogoutModal() {
    document.getElementById("logoutModal").style.display = "none";
}

function confirmLogout() {
    sessionStorage.clear();
    window.location.href = '/';
}


function closeIdleModal() {
    // const idleModal = document.getElementById("idleModal");
    // idleModal.style.display = 'none';
}

function cancelIdleCountdown() {
    clearInterval(idleCountdownInterval);      // 🛑 Stop the countdown
    closeIdleModal();                          // ❌ Close the modal

    sessionStartTime = Math.floor(Date.now() / 1000);  // ✅ Reset session start timestamp

    startTimer();                              // ▶️ Resume timer
    setState('work');                          // 🔄 Change UI back to "work"
    showToast("⏱️ Countdown canceled. Back to work!", "success");
}



