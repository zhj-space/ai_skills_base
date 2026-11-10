"""从 wiki 知识节点导出关系图谱数据，并生成自包含 HTML。

产出：D:/workspace/ai_kb_base/graph.html（双击可看，无外部依赖）
用法：python export_graph.py
"""
import io
import json
import os
import re
import collections

KB = r"D:/workspace/ai_kb_base/second-brain"
OUT = r"D:/workspace/ai_kb_base/graph.html"
DIRS = ["concepts", "entities", "methods", "metrics"]

# 关系族：结构边（默认显示） / 弱边（默认隐藏）
STRUCT = {"broader", "narrower", "has_part", "part_of", "requires", "enables",
          "produces", "produced_by", "applies_to", "applied_by",
          "instance_of", "has_instance", "evolves_to", "evolved_from"}
WEAK = {"related_to"}
SKIP = {"source"}          # 出处文档：指向 summaries，不进主图

LABEL_CN = {
    "broader": "上位", "narrower": "下位", "has_part": "组成", "part_of": "部分于",
    "requires": "前置", "enables": "后继", "produces": "产出", "produced_by": "由产出",
    "applies_to": "应用", "applied_by": "被应用", "instance_of": "实例",
    "has_instance": "实例化", "evolves_to": "演进", "evolved_from": "前身",
    "related_to": "相关", "source": "出处",
}


def main():
    nodes, raw_edges = {}, []
    for d in DIRS:
        p = os.path.join(KB, "wiki", d)
        if not os.path.isdir(p):
            continue
        for f in sorted(os.listdir(p)):
            if not f.endswith(".md"):
                continue
            name = f[:-3]
            s = io.open(os.path.join(p, f), encoding="utf-8").read()
            mt = re.search(r"^type:[ \t]*(\S+)", s, re.M)
            me = re.search(r"^entity_type:[ \t]*(\S+)", s, re.M)
            mq = re.search(r"^> (.+)$", s, re.M)
            nodes[name] = {
                "id": name,
                "type": mt.group(1) if mt else "?",
                "sub": me.group(1) if me else "",
                "brief": (mq.group(1).strip()[:60] if mq else ""),
            }
            seg = s.split("## 关系")[1].split("\n## ")[0] if "## 关系" in s else ""
            for ln in seg.split("\n"):
                t = ln.strip()
                if not t.startswith("- "):
                    continue
                m = re.match(r"^-\s*([^：:]{1,24})\s*[：:]", t)
                if not m:
                    continue
                label = m.group(1).strip()
                for tgt in re.findall(r"\[\[([^\]|#]+)", t):
                    raw_edges.append((name, label, tgt.strip()))

    links, dropped, seen = [], collections.Counter(), set()
    for s, label, t in raw_edges:
        if label in SKIP:
            dropped["出处文档（指向证据页）"] += 1
            continue
        if t not in nodes:
            dropped["目标不在知识节点内"] += 1
            continue
        if s == t:
            dropped["自指"] += 1
            continue
        key = (s, label, t)
        if key in seen:
            dropped["重复"] += 1
            continue
        seen.add(key)
        links.append({"s": s, "t": t, "r": label,
                      "cn": LABEL_CN.get(label, label),
                      "w": 0 if label in WEAK else 1})

    deg = collections.Counter()
    for l in links:
        deg[l["s"]] += 1
        deg[l["t"]] += 1
    for n in nodes.values():
        n["deg"] = deg[n["id"]]

    data = {
        "nodes": sorted(nodes.values(), key=lambda x: -x["deg"]),
        "links": links,
        "meta": {
            "nodes": len(nodes),
            "links": len(links),
            "struct": sum(1 for l in links if l["w"] == 1),
            "weak": sum(1 for l in links if l["w"] == 0),
            "types": dict(collections.Counter(n["type"] for n in nodes.values())),
            "dropped": dict(dropped),
        },
    }

    html = TPL.replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
    io.open(OUT, "w", encoding="utf-8", newline="").write(html)

    print("节点 %d · 边 %d（结构 %d / 弱边 %d）"
          % (data["meta"]["nodes"], data["meta"]["links"],
             data["meta"]["struct"], data["meta"]["weak"]))
    print("类型：", data["meta"]["types"])
    if dropped:
        print("已排除：", dict(dropped))
    print("输出：%s（%.0f KB）" % (OUT, os.path.getsize(OUT) / 1024))


TPL = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>知识库关系图谱</title>
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; overflow: hidden;
    background: #14161a; color: #e8e8ea;
    font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; }
  #wrap { display: flex; height: 100%; }
  #side { width: 288px; flex: 0 0 288px; border-right: 1px solid #2a2d35;
    padding: 16px; overflow-y: auto; background: #191c22; }
  #cv { flex: 1; display: block; cursor: grab; }
  #cv.drag { cursor: grabbing; }
  h1 { font-size: 14px; font-weight: 500; margin: 0 0 4px; }
  .sub { font-size: 11px; color: #8b8f99; line-height: 1.7; margin-bottom: 14px; }
  .stat { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
  .chip { font-size: 11px; padding: 3px 8px; border-radius: 10px;
    border: 1px solid #333742; color: #b9bdc7; }
  .sec { font-size: 11px; color: #8b8f99; margin: 16px 0 8px;
    text-transform: uppercase; letter-spacing: .06em; }
  .lg { display: flex; align-items: center; gap: 8px; font-size: 12px;
    padding: 4px 0; color: #c8ccd6; }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex: 0 0 10px; }
  input[type=text] { width: 100%; padding: 7px 9px; font-size: 12px;
    background: #22262e; border: 1px solid #333742; border-radius: 8px;
    color: #e8e8ea; outline: none; }
  input[type=text]:focus { border-color: #4a5060; }
  label.ck { display: flex; align-items: center; gap: 7px; font-size: 12px;
    color: #c8ccd6; padding: 5px 0; cursor: pointer; }
  input[type=checkbox] { accent-color: #7F77DD; }
  #info { font-size: 12px; line-height: 1.7; color: #c8ccd6; }
  #info .nm { font-size: 14px; font-weight: 500; color: #fff; }
  #info .tp { font-size: 11px; color: #8b8f99; margin-bottom: 8px; }
  #info ul { margin: 6px 0 0; padding-left: 16px; }
  #info li { margin: 3px 0; }
  #info .rl { color: #8b8f99; }
  #hint { position: absolute; right: 14px; bottom: 12px; font-size: 11px;
    color: #5d626e; }
  #panel { position: relative; }
</style>
</head>
<body>
<div id="wrap">
  <div id="side">
    <h1>知识库关系图谱</h1>
    <div class="sub" id="meta"></div>
    <div class="stat" id="typechips"></div>

    <div class="sec">搜索</div>
    <input type="text" id="q" placeholder="输入名称，如 HDFS / 极限">

    <div class="sec">显示</div>
    <label class="ck"><input type="checkbox" id="weak"> 弱关系（相关 · 一半的边）</label>
    <label class="ck"><input type="checkbox" id="labels"> 关系标签</label>
    <label class="ck"><input type="checkbox" id="isolate"> 只看选中节点的邻居</label>

    <div class="sec">节点类型</div>
    <div id="legend"></div>

    <div class="sec">详情</div>
    <div id="info">点击图上任意节点</div>
  </div>
  <div id="panel" style="flex:1;position:relative">
    <canvas id="cv"></canvas>
    <div id="hint">拖拽节点 · 滚轮缩放 · 空白处拖动平移</div>
  </div>
</div>

<script>
const DATA = /*__DATA__*/;

const COLOR = {
  concept: '#7F77DD', entity: '#5DCAA5', method: '#F0997B', metric: '#EF9F27'
};
const RELCOLOR = {
  broader: '#8b83e8', narrower: '#8b83e8',
  has_part: '#5DCAA5', part_of: '#5DCAA5',
  requires: '#EF9F27', enables: '#EF9F27',
  produces: '#F0997B', produced_by: '#F0997B',
  applies_to: '#8b93a8', applied_by: '#8b93a8',
  instance_of: '#4ec9e0', has_instance: '#4ec9e0',
  related_to: '#3d424e'
};

const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
let W = 0, H = 0, DPR = window.devicePixelRatio || 1;

function resize() {
  const r = cv.parentElement.getBoundingClientRect();
  W = r.width; H = r.height;
  cv.width = W * DPR; cv.height = H * DPR;
  cv.style.width = W + 'px'; cv.style.height = H + 'px';
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  draw();
}
window.addEventListener('resize', resize);

const N = {}, ORDER = [];
DATA.nodes.forEach((n, i) => {
  const a = (i / DATA.nodes.length) * Math.PI * 2;
  const rad = 120 + (i % 7) * 34;
  N[n.id] = {
    id: n.id, type: n.type, sub: n.sub, brief: n.brief, deg: n.deg,
    x: Math.cos(a) * rad, y: Math.sin(a) * rad,
    vx: 0, vy: 0, fx: null, fy: null
  };
  ORDER.push(N[n.id]);
});
DATA.links.forEach(l => { l.sn = N[l.s]; l.tn = N[l.t]; });

let zoom = 1, ox = 0, oy = 0;
let sel = null, hover = null;
let showWeak = false, showLabels = false, isolate = false, filterText = '';

function visibleLinks() {
  return DATA.links.filter(l => {
    if (l.w === 0 && !showWeak) return false;
    if (filterText) {
      const q = filterText.toLowerCase();
      if (!(l.sn.id.toLowerCase().includes(q) || l.tn.id.toLowerCase().includes(q))) return false;
    }
    if (isolate && sel) {
      if (l.sn !== sel && l.tn !== sel) return false;
    }
    return true;
  });
}

function neighborsOf(node) {
  const s = new Set();
  DATA.links.forEach(l => {
    if (l.sn === node) s.add(l.tn);
    if (l.tn === node) s.add(l.sn);
  });
  return s;
}

let alpha = 1;
function tick() {
  if (alpha < 0.004) return;
  alpha *= 0.985;
  const nodes = ORDER;
  const k = 5200;
  for (let i = 0; i < nodes.length; i++) {
    const a = nodes[i];
    for (let j = i + 1; j < nodes.length; j++) {
      const b = nodes[j];
      let dx = b.x - a.x, dy = b.y - a.y;
      let d2 = dx * dx + dy * dy;
      if (d2 < 1) { dx = (Math.random() - .5); dy = (Math.random() - .5); d2 = 1; }
      const f = k / d2;
      const d = Math.sqrt(d2);
      const fx = dx / d * f, fy = dy / d * f;
      a.vx -= fx; a.vy -= fy; b.vx += fx; b.vy += fy;
    }
  }
  DATA.links.forEach(l => {
    const a = l.sn, b = l.tn;
    const dx = b.x - a.x, dy = b.y - a.y;
    const d = Math.sqrt(dx * dx + dy * dy) || 1;
    const rest = l.w === 1 ? 88 : 150;
    const f = (d - rest) * (l.w === 1 ? 0.045 : 0.012);
    const fx = dx / d * f, fy = dy / d * f;
    a.vx += fx; a.vy += fy; b.vx -= fx; b.vy -= fy;
  });
  nodes.forEach(n => {
    n.vx -= n.x * 0.0016;
    n.vy -= n.y * 0.0016;
    if (n.fx !== null) { n.x = n.fx; n.y = n.fy; n.vx = n.vy = 0; return; }
    n.vx *= 0.82; n.vy *= 0.82;
    n.x += n.vx; n.y += n.vy;
  });
  draw();
  requestAnimationFrame(tick);
}

function baseR(n) { return 4 + Math.min(9, Math.sqrt(n.deg) * 1.5); }

function draw() {
  ctx.clearRect(0, 0, W, H);
  ctx.save();
  ctx.translate(W / 2 + ox, H / 2 + oy);
  ctx.scale(zoom, zoom);

  const nb = sel ? neighborsOf(sel) : null;
  const q = filterText.toLowerCase();
  const match = n => !q || n.id.toLowerCase().includes(q);

  visibleLinks().forEach(l => {
    const active = !sel || l.sn === sel || l.tn === sel;
    const dim = (sel && !active) || (q && !(match(l.sn) || match(l.tn)));
    ctx.strokeStyle = RELCOLOR[l.r] || '#3d424e';
    ctx.globalAlpha = dim ? 0.07 : (l.w === 1 ? 0.55 : 0.25);
    ctx.lineWidth = (l.w === 1 ? 1.1 : 0.7) / zoom;
    ctx.beginPath();
    ctx.moveTo(l.sn.x, l.sn.y);
    ctx.lineTo(l.tn.x, l.tn.y);
    ctx.stroke();

    if (showLabels && !dim && zoom > 0.7) {
      const mx = (l.sn.x + l.tn.x) / 2, my = (l.sn.y + l.tn.y) / 2;
      ctx.globalAlpha = 0.75;
      ctx.fillStyle = RELCOLOR[l.r] || '#6b7280';
      ctx.font = (10 / zoom) + 'px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(l.cn, mx, my - 3 / zoom);
    }
  });
  ctx.globalAlpha = 1;

  ORDER.forEach(n => {
    const isSel = n === sel, isHover = n === hover;
    const near = !nb || nb.has(n) || isSel;
    const hit = match(n);
    let a = 1;
    if (sel && !near) a = 0.18;
    if (q && !hit) a = 0.12;
    const r = baseR(n) * (isSel ? 1.7 : 1);
    ctx.globalAlpha = a;
    ctx.beginPath();
    ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
    ctx.fillStyle = COLOR[n.type] || '#888';
    ctx.fill();
    if (isSel || isHover) {
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1.6 / zoom;
      ctx.stroke();
    }
    if ((zoom > 0.85 || isSel || isHover || (q && hit)) && a > 0.3) {
      ctx.globalAlpha = Math.min(1, a + 0.25);
      ctx.fillStyle = '#d8dce6';
      ctx.font = ((isSel ? 13 : 11) / zoom) + 'px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(n.id, n.x, n.y + r + 12 / zoom);
    }
  });
  ctx.globalAlpha = 1;
  ctx.restore();
}

function toWorld(ev) {
  const r = cv.getBoundingClientRect();
  const px = ev.clientX - r.left, py = ev.clientY - r.top;
  return { x: (px - W / 2 - ox) / zoom, y: (py - H / 2 - oy) / zoom, px, py };
}

function pick(p) {
  let best = null, bd = 1e9;
  ORDER.forEach(n => {
    const d = Math.hypot(n.x - p.x, n.y - p.y);
    const hit = baseR(n) + 6 / zoom;
    if (d < hit && d < bd) { bd = d; best = n; }
  });
  return best;
}

let dragging = null, panning = false, last = null;
cv.addEventListener('mousedown', ev => {
  const p = toWorld(ev);
  const n = pick(p);
  if (n) { dragging = n; n.fx = n.x; n.fy = n.y; }
  else { panning = true; last = { x: ev.clientX, y: ev.clientY }; cv.classList.add('drag'); }
});
window.addEventListener('mousemove', ev => {
  if (dragging) {
    const p = toWorld(ev);
    dragging.fx = p.x; dragging.fy = p.y;
    dragging.x = p.x; dragging.y = p.y;
    if (alpha < 0.02) { alpha = 0.35; requestAnimationFrame(tick); }
    draw();
    return;
  }
  if (panning && last) {
    ox += ev.clientX - last.x; oy += ev.clientY - last.y;
    last = { x: ev.clientX, y: ev.clientY };
    draw();
    return;
  }
  const n = pick(toWorld(ev));
  if (n !== hover) { hover = n; cv.style.cursor = n ? 'pointer' : 'grab'; draw(); }
});
window.addEventListener('mouseup', ev => {
  if (dragging) {
    const p = toWorld(ev);
    const moved = Math.hypot(dragging.x - p.x, dragging.y - p.y) > 6;
    dragging.fx = null; dragging.fy = null;
    if (!moved) select(dragging);
    dragging = null;
    alpha = Math.max(alpha, 0.12);
    requestAnimationFrame(tick);
  }
  if (panning) { panning = false; cv.classList.remove('drag'); }
});
cv.addEventListener('wheel', ev => {
  ev.preventDefault();
  const before = toWorld(ev);
  zoom *= ev.deltaY < 0 ? 1.12 : 0.89;
  zoom = Math.max(0.25, Math.min(3.5, zoom));
  const after = toWorld(ev);
  ox += (after.x - before.x) * zoom;
  oy += (after.y - before.y) * zoom;
  draw();
}, { passive: false });

const info = document.getElementById('info');
function select(n) {
  sel = (sel === n) ? null : n;
  if (!sel) {
    info.textContent = '点击图上任意节点';
    draw();
    return;
  }
  const outs = DATA.links.filter(l => l.sn === sel);
  const ins = DATA.links.filter(l => l.tn === sel);
  const fmt = arr => arr.map(l => {
    const other = l.sn === sel ? l.tn.id : l.sn.id;
    const dir = l.sn === sel ? '→' : '←';
    return '<li><span class="rl">' + l.cn + '</span> ' + dir + ' ' + other + '</li>';
  }).join('');
  info.innerHTML =
    '<div class="nm">' + sel.id + '</div>' +
    '<div class="tp">' + sel.type + (sel.sub ? ' · ' + sel.sub : '') +
    ' · 度数 ' + sel.deg + '</div>' +
    (sel.brief ? '<div style="color:#9aa0ac">' + sel.brief + '</div>' : '') +
    (outs.length ? '<ul>' + fmt(outs) + '</ul>' : '') +
    (ins.length ? '<div style="margin-top:8px;color:#8b8f99;font-size:11px">被引用</div><ul>' + fmt(ins) + '</ul>' : '');
  draw();
}

document.getElementById('q').addEventListener('input', e => {
  filterText = e.target.value.trim();
  if (filterText) {
    const q = filterText.toLowerCase();
    const hit = ORDER.find(n => n.id.toLowerCase().includes(q));
    if (hit) select(null);
  }
  alpha = Math.max(alpha, 0.1);
  requestAnimationFrame(tick);
  draw();
});
document.getElementById('weak').addEventListener('change', e => {
  showWeak = e.target.checked; draw();
});
document.getElementById('labels').addEventListener('change', e => {
  showLabels = e.target.checked; draw();
});
document.getElementById('isolate').addEventListener('change', e => {
  isolate = e.target.checked; draw();
});

const m = DATA.meta;
document.getElementById('meta').innerHTML =
  m.nodes + ' 个知识节点 · ' + m.struct + ' 条结构关系' +
  (m.weak ? ' · ' + m.weak + ' 条弱关系（默认隐藏）' : '');
document.getElementById('typechips').innerHTML = Object.entries(m.types)
  .map(([k, v]) => '<span class="chip">' + k + ' ' + v + '</span>').join('');

const LEGEND = [
  ['concept', '概念（范式 / 模型 / 机制）'],
  ['entity', '实体（具体产品）'],
  ['method', '方法（可执行步骤）'],
  ['metric', '指标（可度量口径）']
];
document.getElementById('legend').innerHTML = LEGEND.map(([k, t]) =>
  '<div class="lg"><span class="dot" style="background:' + COLOR[k] + '"></span>' +
  '<span>' + t + '</span></div>').join('');

resize();
requestAnimationFrame(tick);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
