/* 芯片设计智能体团队 - 前端交互 */
"use strict";

document.querySelectorAll('.tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('view-' + btn.dataset.view).classList.add('active');
  });
});

async function api(path, body) {
  const opt = { headers: { 'Content-Type': 'application/json' } };
  if (body !== undefined) opt.method = 'POST', opt.body = JSON.stringify(body);
  const resp = await fetch(path, opt);
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
  return resp.json();
}
function show(el, data) {
  el.classList.remove('hidden');
  el.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
}

/* 架构 */
async function aArch() {
  const r = await api('/api/tasks', { goal: '芯片架构设计', params: { action: 'arch', isa: document.getElementById('archIsa').value, core_name: document.getElementById('archName').value } });
  show(document.getElementById('aResult'), r.results[0].result);
}
async function aMicro() {
  const r = await api('/api/tasks', { goal: '微架构设计', params: { action: 'microarch' } });
  show(document.getElementById('aResult'), r.results[0].result);
}
async function aPpa() {
  const r = await api('/api/tasks', { goal: 'PPA 评估', params: { action: 'ppa' } });
  show(document.getElementById('aResult'), r.results[0].result);
}

/* RTL */
async function rModule() {
  const r = await api('/api/tasks', { goal: 'RTL 模块设计', params: { action: 'module', module_name: document.getElementById('rtlName').value, lang: document.getElementById('rtlLang').value } });
  show(document.getElementById('rResult'), r.results[0].result);
}
async function rCode() {
  const r = await api('/api/tasks', { goal: 'RTL 代码生成', params: { action: 'code', module_name: 'cncore_alu', lang: 'SystemVerilog' } });
  show(document.getElementById('rResult'), r.results[0].result);
}
async function rLint() {
  const r = await api('/api/tasks', { goal: 'RTL Lint', params: { action: 'lint' } });
  show(document.getElementById('rResult'), r.results[0].result);
}

/* 验证 */
async function vPlan() {
  const r = await api('/api/tasks', { goal: '验证计划', params: { action: 'plan', block: 'cncore_exu' } });
  show(document.getElementById('vResult'), r.results[0].result);
}
async function vUvm() {
  const r = await api('/api/tasks', { goal: 'UVM 验证环境', params: { action: 'uvm' } });
  show(document.getElementById('vResult'), r.results[0].result);
}
async function vCov() {
  const r = await api('/api/tasks', { goal: '覆盖率形式验证', params: { action: 'cov' } });
  show(document.getElementById('vResult'), r.results[0].result);
}

/* EDA */
async function eSynth() {
  const r = await api('/api/tasks', { goal: '逻辑综合', params: { action: 'synth', block: 'cncore_top' } });
  show(document.getElementById('eResult'), r.results[0].result);
}
async function ePnr() {
  const r = await api('/api/tasks', { goal: '布局布线', params: { action: 'pnr' } });
  show(document.getElementById('eResult'), r.results[0].result);
}
async function eDft() {
  const r = await api('/api/tasks', { goal: 'DFT 设计', params: { action: 'dft' } });
  show(document.getElementById('eResult'), r.results[0].result);
}

/* 流片 */
async function tTapeout() {
  const r = await api('/api/tasks', { goal: '流片签核', params: { action: 'tapeout' } });
  show(document.getElementById('tResult'), r.results[0].result);
}
async function tPackage() {
  const r = await api('/api/tasks', { goal: '封装设计', params: { action: 'package' } });
  show(document.getElementById('tResult'), r.results[0].result);
}
async function tTest() {
  const r = await api('/api/tasks', { goal: 'ATE 测试', params: { action: 'test' } });
  show(document.getElementById('tResult'), r.results[0].result);
}

/* SoC */
async function sSoc() {
  const r = await api('/api/tasks', { goal: 'SoC 集成架构', params: { action: 'soc' } });
  show(document.getElementById('sResult'), r.results[0].result);
}
async function sBoot() {
  const r = await api('/api/tasks', { goal: '启动链路设计', params: { action: 'boot' } });
  show(document.getElementById('sResult'), r.results[0].result);
}
async function sEco() {
  const r = await api('/api/tasks', { goal: '生态协同规划', params: { action: 'ecosystem' } });
  show(document.getElementById('sResult'), r.results[0].result);
}

/* 流水线 */
async function plRun() {
  const r = await api('/api/tasks', { goal: document.getElementById('plGoal').value || '设计自主 CPU 芯片，完成 RTL、验证、EDA、流片与协同规划', params: {} });
  show(document.getElementById('plResult'), r);
}

/* 系统 */
async function loadSystem() {
  try {
    const h = await api('/api/health');
    document.getElementById('sysHealth').textContent = JSON.stringify(h, null, 2);
    const a = await api('/api/agents');
    document.getElementById('sysCards').innerHTML = a.agents.map(x => `<div class="card"><b>${x.name}</b><div class="hint">${x.description}</div></div>`).join('');
  } catch (e) { document.getElementById('sysHealth').textContent = '错误: ' + e.message; }
}
loadSystem();
