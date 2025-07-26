// 获取配置端口
const backendPort = window.envConfig ? window.envConfig.get('BACKEND_PORT') : 8000;

// 采集数据的全局变量
const events = [];
let hoverStart = null;
let hoverPos = null;

// 页面唯一标识
window._test_no_refresh = window._test_no_refresh || Math.random();
console.log('页面唯一标识:', window._test_no_refresh);
console.log('当前后端端口:', backendPort);

// 采集点击事件
document.addEventListener('click', function (e) {
  events.push({
    type: 'click',
    x: e.clientX,
    y: e.clientY,
    timestamp: Date.now() / 1000
  });
  console.log('点击采集:', events[events.length - 1]);
});

// 采集鼠标停留事件
document.addEventListener('mousemove', function (e) {
  const x = e.clientX;
  const y = e.clientY;
  if (!hoverStart || hoverPos.x !== x || hoverPos.y !== y) {
    if (hoverStart) {
      const duration = (Date.now() - hoverStart) / 1000;
      if (duration > 2) {
        events.push({
          type: 'hover',
          x: hoverPos.x,
          y: hoverPos.y,
          duration: duration
        });
        console.log('停留采集:', events[events.length - 1]);
      }
    }
    hoverStart = Date.now();
    hoverPos = { x, y };
  }
});

// 离开页面时结束hover
document.addEventListener('mouseleave', function () {
  if (hoverStart) {
    const duration = (Date.now() - hoverStart) / 1000;
    if (duration > 0.2) {
      events.push({
        type: 'hover',
        x: hoverPos.x,
        y: hoverPos.y,
        duration: duration
      });
      console.log('停留采集:', events[events.length - 1]);
    }
    hoverStart = null;
    hoverPos = null;
  }
});

// 页面离开时上传数据
window.addEventListener('beforeunload', function () {
  uploadEvents();
});

// 定时上传
setInterval(uploadEvents, 10000);

function uploadEvents() {
  if (events.length === 0) return;
  const session_id = getSessionId();
  const page_id = window.location.pathname;
  fetch(`http://localhost:${backendPort}/upload_events`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: session_id,
      page_id: page_id,
      width: window.innerWidth,
      height: window.innerHeight,
      events: events.splice(0, events.length)
    })
  }).then(res => {
    if (res.ok) {
      console.log('数据已上传');
    } else {
      console.error('上传失败', res.status);
    }
  }).catch(err => {
    console.error('上传失败', err);
  });
}

// 简单生成 session_id
function getSessionId() {
  if (!window._session_id) {
    window._session_id = 'sess_' + Math.random().toString(36).slice(2) + '_' + Date.now();
  }
  return window._session_id;
}