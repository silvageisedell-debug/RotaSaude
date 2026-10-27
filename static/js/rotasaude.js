/* RotaSaúde — comportamentos de tela portados do protótipo. As regras ficam no servidor. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const guardar = {
    ler(k) { try { return JSON.parse(localStorage.getItem(k) || "null"); } catch (e) { return null; } },
    gravar(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* sem armazenamento */ } },
    apagar(k) { try { localStorage.removeItem(k); } catch (e) { /* sem armazenamento */ } },
  };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  /* ---------- Mensagens (toasts) ---------- */
  function toast(texto, tipo) {
    let box = $("#toasts");
    if (!box) { box = document.createElement("div"); box.id = "toasts"; document.body.appendChild(box); }
    const t = document.createElement("div");
    t.className = "toast " + (tipo || "");
    t.textContent = texto;
    box.appendChild(t);
    setTimeout(() => t.remove(), 3200);
  }
  window.rsToast = toast;
  $$("#toasts .toast").forEach((t, i) => setTimeout(() => t.remove(), 3200 + i * 400));

  /* ---------- Menu lateral ---------- */
  const app = $("#app");
  const btnRecolher = $("#colb");
  if (app && btnRecolher) {
    if (guardar.ler("rs_menu_mini")) { app.classList.add("mini"); btnRecolher.textContent = "›"; }
    btnRecolher.addEventListener("click", () => {
      app.classList.toggle("mini");
      const mini = app.classList.contains("mini");
      btnRecolher.textContent = mini ? "›" : "‹";
      guardar.gravar("rs_menu_mini", mini);
    });
  }
  let ultimoY = 0;
  addEventListener("scroll", () => {
    const side = $("#side");
    if (!side) return;
    const y = scrollY;
    if (innerWidth < 900) side.classList.toggle("hid", y > ultimoY && y > 90 && !tour.ativo);
    else side.classList.remove("hid");
    ultimoY = y;
  }, { passive: true });

  /* ---------- Tabelas viram cartões no celular ---------- */
  function rotularTabelas() {
    $$("main table").forEach((t) => {
      const cab = $$("thead th", t).map((th) => th.textContent.trim());
      $$("tbody tr", t).forEach((tr) => [...tr.children].forEach((td, i) => {
        if (cab[i] && !td.dataset.label) td.dataset.label = cab[i];
      }));
    });
  }
  rotularTabelas();

  /* ---------- Acordeões de cadastro ---------- */
  $$(".accb").forEach((b) => b.addEventListener("click", () => {
    const f = b.nextElementSibling;
    const abrir = f.hidden;
    f.hidden = !abrir;
    b.setAttribute("aria-expanded", abrir ? "true" : "false");
    if (abrir) { const i = $("input:not([type=hidden]),select,textarea", f); if (i) i.focus({ preventScroll: true }); }
  }));

  /* ---------- Máscaras ---------- */
  const dig = (v) => String(v || "").replace(/\D/g, "");
  const mascaras = {
    cpf: (v) => dig(v).slice(0, 11).replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d{1,2})$/, "$1-$2"),
    cep: (v) => { v = dig(v).slice(0, 8); return v.length > 5 ? v.slice(0, 5) + "-" + v.slice(5) : v; },
    digitos: (v) => dig(v),
    telefone: (v) => {
      v = dig(v).slice(0, 11);
      if (v.length <= 2) return v;
      if (v.length <= 6) return "(" + v.slice(0, 2) + ") " + v.slice(2);
      return "(" + v.slice(0, 2) + ") " + v.slice(2, v.length - 4) + "-" + v.slice(-4);
    },
  };
  $$("[data-mascara]").forEach((el) => {
    const f = mascaras[el.dataset.mascara];
    if (!f) return;
    el.value = f(el.value);
    el.addEventListener("input", () => { el.value = f(el.value); });
  });
  $$("[data-maiusculo]").forEach((el) => el.addEventListener("input", () => {
    el.value = el.value.toUpperCase().replace(/[^A-Z0-9-]/g, "");
  }));

  /* ---------- Confirmações ---------- */
  $$("form[data-confirmar]").forEach((f) => f.addEventListener("submit", (e) => {
    if (!confirm(f.dataset.confirmar)) e.preventDefault();
  }));

  /* ---------- Rascunho: guarda o que está sendo preenchido neste aparelho ---------- */
  const usuarioAtual = document.body.dataset.usuario || "";
  $$("form[data-rascunho]").forEach((form) => {
    const chave = "rs_rascunho:" + usuarioAtual + ":" + location.pathname;
    const campos = () => $$("input,select,textarea", form).filter((c) =>
      c.name && c.type !== "password" && c.type !== "hidden" && c.type !== "submit");
    const ler = () => {
      const dados = {};
      campos().forEach((c) => {
        if (c.type === "checkbox") { (dados[c.name] = dados[c.name] || []); if (c.checked) dados[c.name].push(c.value); }
        else dados[c.name] = c.value;
      });
      return dados;
    };
    const original = JSON.stringify(ler());
    const salvo = guardar.ler(chave);
    const temErro = !!$(".erros, .campo.erro", form);
    if (salvo && JSON.stringify(salvo) !== original && !temErro) {
      const aviso = document.createElement("div");
      aviso.className = "rascunho";
      aviso.innerHTML = '<span>Você tem um preenchimento não enviado nesta tela.</span>' +
        '<button type="button" class="btn em sm" data-acao="retomar">Retomar</button>' +
        '<button type="button" class="btn ghost sm" data-acao="descartar">Descartar</button>';
      form.prepend(aviso);
      aviso.addEventListener("click", (e) => {
        const acao = e.target.dataset.acao;
        if (!acao) return;
        if (acao === "retomar") {
          campos().forEach((c) => {
            if (!(c.name in salvo)) return;
            if (c.type === "checkbox") c.checked = (salvo[c.name] || []).includes(c.value);
            else c.value = salvo[c.name];
          });
          toast("Preenchimento retomado.");
        } else {
          guardar.apagar(chave);
        }
        aviso.remove();
        atualizarSeloRecuperar();
      });
    }
    form.addEventListener("input", () => { guardar.gravar(chave, ler()); atualizarSeloRecuperar(); });
    form.addEventListener("submit", () => guardar.apagar(chave));
  });

  function rascunhosPendentes() {
    const lista = [];
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.startsWith("rs_rascunho:" + usuarioAtual + ":")) lista.push(k.split(":").slice(2).join(":"));
      }
    } catch (e) { /* sem armazenamento */ }
    return lista;
  }
  function atualizarSeloRecuperar() {
    const selo = $("#rcb");
    if (!selo) return;
    const n = rascunhosPendentes().length;
    selo.textContent = n;
    selo.classList.toggle("hide", !n);
  }
  atualizarSeloRecuperar();

  /* ---------- Recuperar (resumo do servidor + rascunhos locais) ---------- */
  const dlg = $("#dlg-recuperar");
  const btnRecuperar = $("#btn-recuperar");
  if (dlg && btnRecuperar) {
    btnRecuperar.addEventListener("click", async () => {
      $(".conteudo", dlg).innerHTML = '<p class="mut">Carregando…</p>';
      dlg.showModal();
      try {
        const r = await fetch(btnRecuperar.dataset.url, { headers: { "X-Requested-With": "fetch" } });
        $(".conteudo", dlg).innerHTML = await r.text();
      } catch (e) {
        $(".conteudo", dlg).innerHTML = '<p class="mut">Sem conexão com o servidor. Os rascunhos abaixo continuam guardados neste aparelho.</p>';
      }
      const telas = rascunhosPendentes();
      const alvo = $("#rascunhos", dlg);
      if (alvo) {
        alvo.innerHTML = telas.length
          ? telas.map((p) => `<div class="rci"><b>${esc(p)}</b><small>Você começou a preencher e não concluiu.</small><a class="btn em sm" href="${esc(p)}">Retomar</a></div>`).join("")
          : '<div class="rci"><small>Nenhum trabalho pela metade.</small></div>';
      }
      const copiar = $("#copiar-resumo", dlg);
      if (copiar) copiar.addEventListener("click", () => {
        const texto = $("#texto-resumo", dlg).value;
        (navigator.clipboard ? navigator.clipboard.writeText(texto) : Promise.reject())
          .then(() => toast("Resumo copiado."), () => toast("Não foi possível copiar.", "error"));
      });
    });
    dlg.addEventListener("click", (e) => { if (e.target === dlg || e.target.dataset.fechar !== undefined) dlg.close(); });
  }

  /* ---------- Tour "Conheça o sistema" ---------- */
  const tour = { ativo: false, i: 0, passos: [] };
  function passosDoTour() {
    const passos = [{ t: "Bem-vindo(a) ao RotaSaúde", d: "Este tour mostra, parte por parte, o que cada coisa faz nesta tela. Use Próximo para avançar." }];
    $$("[data-tour]").forEach((el) => {
      if (el.offsetParent === null && getComputedStyle(el).position !== "fixed") return;
      passos.push({ el, t: el.dataset.tour, d: el.dataset.tourTexto || "" });
    });
    passos.push({ t: "Tudo pronto!", d: "Abra o tour em qualquer tela para ver as explicações daquela área." });
    return passos;
  }
  function tourFim() {
    tour.ativo = false;
    ["tblk", "tspot", "tcard"].forEach((id) => { const d = document.getElementById(id); if (d) d.remove(); });
    removeEventListener("resize", tourPosicionar);
    removeEventListener("scroll", tourPosicionar);
  }
  function tourPosicionar() {
    if (!tour.ativo) return;
    const sp = $("#tspot"), c = $("#tcard"), el = tour.passos[tour.i].el;
    if (!el) { sp.className = "tspot none"; c.style.top = "50%"; c.style.bottom = "auto"; c.style.transform = "translateY(-50%)"; return; }
    const r = el.getBoundingClientRect(), pd = 6;
    sp.className = "tspot";
    sp.style.cssText = `top:${r.top - pd}px;left:${r.left - pd}px;width:${r.width + pd * 2}px;height:${r.height + pd * 2}px`;
    c.style.transform = "none";
    if (r.top + r.height / 2 > innerHeight * 0.5) { c.style.top = "calc(env(safe-area-inset-top,0px) + 12px)"; c.style.bottom = "auto"; }
    else { c.style.top = "auto"; c.style.bottom = "76px"; }
  }
  function tourIr(i) {
    const n = tour.passos.length;
    if (i < 0 || i >= n) return tourFim();
    tour.i = i;
    const p = tour.passos[i];
    const c = $("#tcard");
    c.innerHTML = `<button class="tx" aria-label="Fechar" data-t="fim">×</button><div class="tn">${i + 1} / ${n}</div><h4>${esc(p.t)}</h4><p>${esc(p.d)}</p><div class="tb">${i > 0 ? '<button class="btn ghost sm" data-t="ant">Anterior</button>' : ""}<button class="btn em sm" data-t="${i < n - 1 ? "prox" : "fim"}">${i < n - 1 ? "Próximo" : "Concluir"}</button></div>`;
    if (p.el) {
      $("#side") && $("#side").classList.remove("hid");
      if (p.el.closest("#side,#road")) p.el.scrollIntoView({ block: "nearest", inline: "center" });
      else p.el.scrollIntoView({ block: p.el.getBoundingClientRect().height > innerHeight * 0.45 ? "start" : "center" });
    }
    setTimeout(tourPosicionar, 120);
  }
  const btnTour = $("#btn-tour");
  if (btnTour) btnTour.addEventListener("click", () => {
    tourFim();
    tour.ativo = true;
    tour.passos = passosDoTour();
    ["tblk", "tspot", "tcard"].forEach((id) => { const d = document.createElement("div"); d.id = id; d.className = id; document.body.appendChild(d); });
    $("#tcard").addEventListener("click", (e) => {
      const a = e.target.dataset.t;
      if (a === "prox") tourIr(tour.i + 1); else if (a === "ant") tourIr(tour.i - 1); else if (a === "fim") tourFim();
    });
    addEventListener("resize", tourPosicionar);
    addEventListener("scroll", tourPosicionar, { passive: true });
    tourIr(0);
  });
  addEventListener("keydown", (e) => { if (e.key === "Escape" && tour.ativo) tourFim(); });

  /* ---------- Programar viagem: lista flutuante de disponibilidade ---------- */
  const prog = $("#form-programar");
  if (prog) {
    const url = prog.dataset.disponibilidade;
    const campo = (n) => prog.elements[n];
    let cache = null;
    const linha = (alvo, x, selecionado) => `<div class="plr ${x.livre ? "" : "off"} ${String(x.id) === selecionado ? "sel" : ""}" ${x.livre ? `data-alvo="${alvo}" data-id="${x.id}"` : ""} role="option"><i style="background:${x.livre ? "#16A34A" : "#E11D48"}"></i><div><b>${esc(x.nome)}</b><small>${esc(x.info || "")}</small></div><span style="font-weight:700;font-size:12px;color:${x.livre ? "#16A34A" : "#E11D48"}">${esc(x.status)}</span></div>`;
    function janela() {
      const s = campo("saida").value, d = Math.max(1, parseInt(campo("duracao_horas").value || "1", 10));
      const [h, m] = s.split(":").map(Number), fim = h * 60 + m + d * 60;
      const data = campo("data").value.split("-").reverse().join("/");
      return `${data}, das ${s} às ${String(Math.floor(fim / 60)).padStart(2, "0")}:${String(fim % 60).padStart(2, "0")}`;
    }
    function aplicar() {
      if (!cache) return;
      [["veiculo", cache.veiculos, "Veículos"], ["motorista", cache.motoristas, "Motoristas"]].forEach(([nome, itens, rotulo]) => {
        const sel = campo(nome);
        const livres = new Set(itens.filter((x) => x.livre).map((x) => String(x.id)));
        [...sel.options].forEach((o) => {
          if (!o.value) return;
          const x = itens.find((y) => String(y.id) === o.value);
          o.disabled = !livres.has(o.value);
          if (x) o.textContent = `${x.nome} — ${x.status}`;
        });
        if (sel.value && !livres.has(sel.value)) sel.value = "";
        const lista = $("#lista-" + nome);
        lista.innerHTML = `<div class="plh">${rotulo} em ${janela()}:</div>` + itens.map((x) => linha(nome, x, sel.value)).join("") +
          (livres.size ? "" : `<div class="plh" style="color:#E11D48">Nenhum livre nesse horário. Mude a data, a saída ou a duração.</div>`);
      });
      const nv = cache.veiculos.filter((x) => x.livre).length, nm = cache.motoristas.filter((x) => x.livre).length;
      $("#resumo-disponibilidade").textContent = `${nv} de ${cache.veiculos.length} veículos e ${nm} de ${cache.motoristas.length} motoristas disponíveis em ${janela()}.`;
    }
    async function atualizar() {
      if (!campo("data").value) return;
      const q = new URLSearchParams({ data: campo("data").value, saida: campo("saida").value, duracao: campo("duracao_horas").value || "1" });
      try { cache = await (await fetch(url + "?" + q)).json(); aplicar(); } catch (e) { /* o servidor valida de qualquer forma */ }
    }
    const fechar = () => $$(".plo", prog).forEach((l) => { l.classList.add("hide"); l.parentNode.classList.remove("open"); });
    $$(".selw", prog).forEach((w) => {
      const abrir = () => {
        const lista = $("#lista-" + w.dataset.campo), estava = lista.classList.contains("hide");
        fechar();
        if (estava) { aplicar(); lista.classList.remove("hide"); lista.parentNode.classList.add("open"); }
      };
      w.addEventListener("click", abrir);
      w.addEventListener("keydown", (e) => { if (["Enter", " ", "ArrowDown"].includes(e.key)) { e.preventDefault(); abrir(); } });
    });
    prog.addEventListener("click", (e) => {
      const item = e.target.closest(".plr[data-id]");
      if (item) { campo(item.dataset.alvo).value = item.dataset.id; fechar(); aplicar(); }
    });
    document.addEventListener("click", (e) => { if (!e.target.closest(".dd")) fechar(); });
    addEventListener("keydown", (e) => { if (e.key === "Escape") fechar(); });
    ["data", "saida", "duracao_horas"].forEach((n) => campo(n).addEventListener("change", atualizar));
    campo("duracao_horas").addEventListener("input", atualizar);
    atualizar();
  }

  /* ---------- Caderno ---------- */
  const folha = $("#folha-caderno");
  if (folha) {
    $$(".cd", folha).forEach((b) => b.addEventListener("click", () => {
      $$(".cd", folha).forEach((x) => x.classList.toggle("on", x === b));
      folha.elements.cor.value = b.dataset.cor;
    }));
    const pin = $("#npin");
    if (pin) pin.addEventListener("click", () => {
      const on = !pin.classList.contains("on");
      pin.classList.toggle("on", on);
      folha.elements.fixada.value = on ? "True" : "False";
    });
    $$("[data-lembrar]", folha).forEach((b) => b.addEventListener("click", () => {
      folha.elements.lembrar_em.value = b.dataset.lembrar;
    }));
  }
  const dlgLembrete = $("#dlg-lembrete");
  if (dlgLembrete && dlgLembrete.showModal) dlgLembrete.showModal();

  /* ---------- Gráfico do painel ---------- */
  const dadosGrafico = $("#dados-grafico");
  if (dadosGrafico && window.Chart) {
    const d = JSON.parse(dadosGrafico.textContent);
    Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue("--mut");
    new Chart($("#grafico-status"), {
      type: "doughnut",
      data: { labels: d.rotulos, datasets: [{ data: d.valores, backgroundColor: d.cores, borderRadius: 8 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } },
    });
  }
})();
