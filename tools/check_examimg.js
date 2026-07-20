#!/usr/bin/env node
// 題本圖片一致性檢查：node tools/check_examimg.js
// - EXAM_IMG 登錄的每個檔案都存在於 img/<回數>/
// - img/ 裡沒有未登錄的孤兒檔
// - 題組（q起-迄.png）三個題號都要指向同一檔
// - 覆蓋率：每個已登錄回數的 Part 1（1–6 題）與題庫中所有
//   「Look at the graphic」圖表題是否都有圖（缺的列出來，不算錯誤）
// 硬錯誤 exit 1（缺檔/登錄不一致），只有覆蓋缺口則 exit 0。
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const load = (f, name) => new Function(fs.readFileSync(path.join(ROOT, 'data', f), 'utf8') + `; return ${name};`)();

const IMG = load('examimg.js', 'EXAM_IMG');
const LQ = Object.assign({}, load('exam_ez34.js', 'EZ_LQ'), load('exam_blue.js', 'BLUE_LQ'));
let errors = 0;

for (const [test, mp] of Object.entries(IMG)) {
  const dir = path.join(ROOT, 'img', test);
  // 登錄檔都存在
  for (const [q, f] of Object.entries(mp)) {
    if (!fs.existsSync(path.join(dir, f))) { console.log(`✗ ${test} 第 ${q} 題登錄的 ${f} 不存在`); errors++; }
  }
  // 沒有孤兒檔
  const used = new Set(Object.values(mp));
  for (const f of fs.existsSync(dir) ? fs.readdirSync(dir) : []) {
    if (f.endsWith('.png') && !used.has(f)) { console.log(`✗ img/${test}/${f} 沒有登錄進 EXAM_IMG`); errors++; }
  }
  // 題組檔名 q起-迄：範圍內每個題號都要登錄且指向同一檔
  for (const f of used) {
    const m = f.match(/^q(\d+)-(\d+)\.png$/);
    if (!m) continue;
    for (let q = +m[1]; q <= +m[2]; q++) {
      if (mp[q] !== f) { console.log(`✗ ${test} 第 ${q} 題應指向 ${f}（題組共用），實際是 ${mp[q] || '未登錄'}`); errors++; }
    }
  }
  // 覆蓋率（提示用）：P1 全 6 題＋題庫的圖表題
  const missing = [];
  for (let q = 1; q <= 6; q++) if (!mp[q]) missing.push(q);
  const D = LQ[test] || {};
  for (const [q, item] of Object.entries(D)) {
    if (/look at the graphic/i.test(item.q) && !mp[q]) missing.push(q);
  }
  console.log(`${test}: 登錄 ${Object.keys(mp).length} 題、${used.size} 檔` +
    (missing.length ? `｜還缺：${missing.join(', ')}` : '｜P1 與圖表題已齊'));
}
console.log(errors ? `✗ ${errors} 個錯誤` : '✓ 檢查通過');
process.exit(errors ? 1 : 0);
