from __future__ import annotations

import json
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
ASSET_LOGO = ROOT / "assets" / "logo.png"
DATA_FILE = ROOT / "liga_data.json"

ROSTERS = {
    "JNKA": [
        "Chelsea F.C", "A.C. Milan", "AS Roma", "Manchester United",
        "Fenerbahçe SK", "River Plate", "Real Sociedad", "FC Porto",
    ],
    "Mati": [
        "Manchester City", "FC Barcelona", "PSG", "Sporting Clube",
        "Inter de Milán", "Real Madrid", "Borussia Dortmund", "Nottingham Forest",
    ],
    "Maxi": [
        "Liverpool FC", "SL Benfica", "Atlético de Madrid", "Real Betis",
        "Napoli", "Aston Villa", "Juventus", "Boca Juniors",
    ],
}
TEAMS = [team for roster in ROSTERS.values() for team in roster]
TEAM_OWNER = {team: owner for owner, roster in ROSTERS.items() for team in roster}
ROUND_IDS = [str(i) for i in range(1, 9)]

st.set_page_config(page_title="Liga MJ | Centro de competición", page_icon="⚽", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');
    :root { --bg:#080c12; --panel:#111923; --panel2:#0d141d; --cyan:#08d9e8; --cyan2:#00a9c1; --text:#f3f7fb; --muted:#91a0b2; --line:rgba(139,165,184,.16); }
    html, body, [class*="css"] { font-family: Inter, sans-serif; }
    .stApp { background: radial-gradient(ellipse at 80% -15%, rgba(0,217,232,.13), transparent 34%), var(--bg); color:var(--text); }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#0d151e 0%,#080c12 100%); border-right:1px solid var(--line); }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#c5d0da; }
    h1,h2,h3 { font-family:'Barlow Condensed',sans-serif !important; letter-spacing:.3px; }
    h1 { font-size:3rem !important; line-height:1 !important; font-weight:800 !important; }
    h2 { font-size:2rem !important; font-weight:700 !important; }
    h3 { font-size:1.35rem !important; font-weight:700 !important; }
    .hero { padding:26px 30px; border:1px solid rgba(8,217,232,.23); border-radius:22px; background:linear-gradient(115deg,rgba(8,217,232,.12),rgba(16,26,37,.96) 50%,rgba(17,25,35,.93)); box-shadow:0 18px 50px rgba(0,0,0,.18); margin:2px 0 20px; }
    .eyebrow { color:var(--cyan); font-size:.74rem; font-weight:800; letter-spacing:2.5px; text-transform:uppercase; }
    .hero-title { font:800 2.6rem 'Barlow Condensed',sans-serif; margin:.25rem 0 .4rem; color:#fff; }
    .hero-sub { color:#afbdca; font-size:.96rem; margin:0; }
    .section-label { color:var(--cyan); text-transform:uppercase; letter-spacing:2px; font-weight:800; font-size:.72rem; margin:15px 0 8px; }
    .metric-card { background:linear-gradient(145deg,#121c27,#0d141d); border:1px solid var(--line); border-radius:16px; padding:17px 18px; min-height:112px; }
    .metric-label { color:var(--muted); font-size:.74rem; text-transform:uppercase; letter-spacing:1.2px; font-weight:700; }
    .metric-value { font:800 2.1rem 'Barlow Condensed',sans-serif; margin-top:4px; color:#fff; }
    .metric-hint { color:var(--cyan); font-size:.75rem; margin-top:1px; }
    .surface { background:linear-gradient(150deg,rgba(18,28,39,.96),rgba(12,19,27,.96)); border:1px solid var(--line); border-radius:16px; padding:18px 20px; margin-bottom:12px; }
    .owner-card { background:#101923; border:1px solid var(--line); border-radius:14px; padding:16px; height:100%; }
    .owner-name { color:var(--cyan); text-transform:uppercase; font-weight:800; letter-spacing:1.5px; font-size:.76rem; }
    .owner-list { color:#d8e1e9; line-height:1.85; font-size:.89rem; margin-top:8px; }
    .pill { display:inline-block; padding:4px 9px; border-radius:100px; font-size:.68rem; font-weight:800; letter-spacing:.5px; margin-left:7px; vertical-align:middle; }
    .pill-cyan { background:rgba(8,217,232,.12); color:#3ce5ee; border:1px solid rgba(8,217,232,.22); }
    .pill-red { background:rgba(242,86,99,.12); color:#ff8d99; border:1px solid rgba(242,86,99,.2); }
    .fixture-head { color:#8fa0b0; text-transform:uppercase; letter-spacing:1.1px; font-size:.68rem; font-weight:800; }
    .fixture-team { color:#f4f7fa; font-weight:700; }
    .fixture-score { color:var(--cyan); font:800 1.2rem 'Barlow Condensed',sans-serif; }
    .bracket-card { background:linear-gradient(145deg,#131e29,#0e151e); border:1px solid var(--line); border-radius:14px; padding:14px 16px; margin:7px 0; }
    .bracket-stage { color:var(--cyan); text-transform:uppercase; letter-spacing:1.5px; font-size:.67rem; font-weight:800; }
    .bracket-teams { font-weight:700; margin-top:7px; line-height:1.7; }
    .bracket-score { color:var(--cyan); font-family:'Barlow Condensed',sans-serif; font-size:1.05rem; font-weight:800; }
    div.stButton > button { border-radius:10px; font-weight:700; border:1px solid rgba(8,217,232,.3); }
    div.stButton > button[kind="primary"] { background:linear-gradient(90deg,#08c8d8,#00a9c1); color:#041015; border:0; }
    div[data-testid="stForm"] { background:#101923; border:1px solid var(--line); border-radius:14px; padding:14px; }
    div[data-testid="stExpander"] { background:#0f1720; border:1px solid var(--line); border-radius:12px; }
    div[data-testid="stAlert"] { border-radius:12px; }
    .small-note { color:#91a0b2; font-size:.8rem; }
    .footer { color:#778797; font-size:.74rem; border-top:1px solid var(--line); margin-top:32px; padding-top:14px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def blank_data() -> dict:
    return {
        "matchdays": {rid: {"title": f"Fecha {int(rid)}", "fixtures": []} for rid in ROUND_IDS},
        "knockout": {},
        "playoff_snapshot": None,
    }


def load_data() -> dict:
    if not DATA_FILE.exists():
        return blank_data()
    try:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        base = blank_data()
        if isinstance(raw, dict):
            for rid in ROUND_IDS:
                if rid in raw.get("matchdays", {}):
                    base["matchdays"][rid].update(raw["matchdays"][rid])
                    if not isinstance(base["matchdays"][rid].get("fixtures"), list):
                        base["matchdays"][rid]["fixtures"] = []
            base["knockout"] = raw.get("knockout", {}) if isinstance(raw.get("knockout", {}), dict) else {}
            base["playoff_snapshot"] = raw.get("playoff_snapshot")
        return base
    except (OSError, json.JSONDecodeError):
        return blank_data()


def save_data() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = DATA_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(DATA_FILE)


def validate_backup(candidate: object) -> dict:
    if not isinstance(candidate, dict) or not isinstance(candidate.get("matchdays"), dict):
        raise ValueError("El archivo no tiene el formato de una copia de Liga MJ.")
    restored = blank_data()
    for rid in ROUND_IDS:
        saved_day = candidate["matchdays"].get(rid)
        if not isinstance(saved_day, dict) or not isinstance(saved_day.get("fixtures"), list):
            raise ValueError(f"Falta la lista de partidos de la Fecha {rid}.")
        restored["matchdays"][rid]["title"] = str(saved_day.get("title") or f"Fecha {rid}")[:80]
        used_teams: set[str] = set()
        for saved in saved_day["fixtures"]:
            if not isinstance(saved, dict):
                raise ValueError("Hay un partido con formato inválido.")
            home, away = saved.get("home"), saved.get("away")
            if home not in TEAMS or away not in TEAMS or home == away:
                raise ValueError("La copia incluye un equipo desconocido o un cruce inválido.")
            if home in used_teams or away in used_teams:
                raise ValueError(f"Un equipo aparece más de una vez en la Fecha {rid}.")
            used_teams.update((home, away))
            goals = []
            for key in ("home_goals", "away_goals"):
                value = saved.get(key)
                if value is not None and (not isinstance(value, int) or value < 0):
                    raise ValueError("Los goles deben ser números enteros no negativos.")
                goals.append(value)
            if (goals[0] is None) != (goals[1] is None):
                raise ValueError("Cada partido debe tener ambos goles cargados o ninguno.")
            restored["matchdays"][rid]["fixtures"].append({
                "id": str(saved.get("id") or uuid.uuid4().hex[:10]),
                "home": home, "away": away, "home_goals": goals[0], "away_goals": goals[1],
            })
    allowed_knockout = {"p_5_12", "p_7_10", "p_6_11", "p_8_9", "qf_1", "qf_2", "qf_3", "qf_4", "sf_a", "sf_b", "final"}
    saved_ko = candidate.get("knockout", {})
    if not isinstance(saved_ko, dict) or not set(saved_ko).issubset(allowed_knockout):
        raise ValueError("La sección de eliminatorias tiene un formato no reconocido.")
    for match_id, saved in saved_ko.items():
        if not isinstance(saved, dict) or saved.get("home") not in TEAMS or saved.get("away") not in TEAMS:
            raise ValueError(f"El resultado de eliminatoria {match_id} no es válido.")
        for key in ("home_goals", "away_goals"):
            value = saved.get(key)
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"Los goles de eliminatoria {match_id} no son válidos.")
    restored["knockout"] = saved_ko
    restored["playoff_snapshot"] = candidate.get("playoff_snapshot")
    return restored


def completed_fixtures() -> list[dict]:
    return [
        fixture
        for rid in ROUND_IDS
        for fixture in data["matchdays"][rid]["fixtures"]
        if fixture.get("home_goals") is not None and fixture.get("away_goals") is not None
    ]


def calculate_table() -> list[dict]:
    stats = {
        team: {"team": team, "PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "DG": 0, "Pts": 0}
        for team in TEAMS
    }
    matches = completed_fixtures()
    for match in matches:
        home, away = match["home"], match["away"]
        hg, ag = int(match["home_goals"]), int(match["away_goals"])
        if home not in stats or away not in stats:
            continue
        hs, aws = stats[home], stats[away]
        hs["PJ"] += 1; aws["PJ"] += 1
        hs["GF"] += hg; hs["GC"] += ag
        aws["GF"] += ag; aws["GC"] += hg
        if hg > ag:
            hs["G"] += 1; hs["Pts"] += 3; aws["P"] += 1
        elif hg < ag:
            aws["G"] += 1; aws["Pts"] += 3; hs["P"] += 1
        else:
            hs["E"] += 1; aws["E"] += 1
            hs["Pts"] += 1; aws["Pts"] += 1
    for row in stats.values():
        row["DG"] = row["GF"] - row["GC"]

    def head_to_head_points(team: str, group: list[str]) -> int:
        points = 0
        for match in matches:
            home, away = match["home"], match["away"]
            if home not in group or away not in group or team not in (home, away):
                continue
            hg, ag = int(match["home_goals"]), int(match["away_goals"])
            if hg == ag:
                points += 1
            elif (team == home and hg > ag) or (team == away and ag > hg):
                points += 3
        return points

    def mini_stats(team: str, group: list[str]) -> tuple[int, int, int]:
        pts = gf = gc = 0
        for match in matches:
            home, away = match["home"], match["away"]
            if home not in group or away not in group or team not in (home, away):
                continue
            hg, ag = int(match["home_goals"]), int(match["away_goals"])
            if team == home:
                gf += hg; gc += ag
                pts += 3 if hg > ag else (1 if hg == ag else 0)
            else:
                gf += ag; gc += hg
                pts += 3 if ag > hg else (1 if ag == hg else 0)
        return pts, gf - gc, gf

    def fallback_key(team: str) -> tuple:
        r = stats[team]
        return (-r["DG"], r["GC"], -r["GF"], team.casefold())

    grouped: dict[int, list[str]] = defaultdict(list)
    for team in TEAMS:
        grouped[stats[team]["Pts"]].append(team)
    ordered: list[str] = []
    for points in sorted(grouped, reverse=True):
        group = grouped[points]
        if len(group) == 2:
            a, b = group
            pa, pb = head_to_head_points(a, group), head_to_head_points(b, group)
            if pa != pb:
                ordered.extend([a, b] if pa > pb else [b, a])
                continue
            ordered.extend(sorted(group, key=fallback_key))
        elif len(group) > 2:
            ordered.extend(sorted(group, key=lambda team: (*(-v for v in mini_stats(team, group)), *fallback_key(team))))
        else:
            ordered.extend(group)
    return [{"Pos": idx + 1, **stats[team]} for idx, team in enumerate(ordered)]


def table_snapshot(table: list[dict]) -> str:
    return "|".join(row["team"] for row in table)


def playoff_ready() -> bool:
    return all(data["matchdays"][rid]["fixtures"] for rid in ROUND_IDS) and all(
        fixture.get("home_goals") is not None and fixture.get("away_goals") is not None
        for rid in ROUND_IDS for fixture in data["matchdays"][rid]["fixtures"]
    )


def match_winner(match_id: str, current_pair: tuple[str | None, str | None]) -> str | None:
    saved = data["knockout"].get(match_id)
    if not saved or not all(current_pair) or saved.get("home") != current_pair[0] or saved.get("away") != current_pair[1]:
        return None
    hg, ag = saved.get("home_goals"), saved.get("away_goals")
    if hg is None or ag is None:
        return None
    if int(hg) > int(ag):
        return current_pair[0]
    if int(ag) > int(hg):
        return current_pair[1]
    advancing = saved.get("advancing")
    return advancing if advancing in current_pair else None


def render_match_card(match_id: str, label: str, pair: tuple[str | None, str | None], *, editable: bool) -> None:
    home, away = pair
    saved = data["knockout"].get(match_id, {})
    st.markdown(f'<div class="bracket-card"><div class="bracket-stage">{label}</div><div class="bracket-teams">{home or "Por definir"} <span class="bracket-score">{saved.get("home_goals", "–")} : {saved.get("away_goals", "–")}</span> {away or "Por definir"}</div></div>', unsafe_allow_html=True)
    if not editable or not home or not away:
        return
    # A saved result is only applicable to the exact pair currently shown.
    old = saved if saved.get("home") == home and saved.get("away") == away else {}
    with st.form(f"ko_{match_id}"):
        c1, c2, c3 = st.columns([1, 1, 2])
        hg = c1.number_input(f"Goles · {home}", min_value=0, step=1, value=int(old.get("home_goals") or 0), key=f"{match_id}_hg")
        ag = c2.number_input(f"Goles · {away}", min_value=0, step=1, value=int(old.get("away_goals") or 0), key=f"{match_id}_ag")
        advancing = None
        if hg == ag:
            choices = [home, away]
            selected = old.get("advancing") if old.get("advancing") in choices else home
            advancing = c3.selectbox("Si empatan, ¿quién avanza?", choices, index=choices.index(selected), key=f"{match_id}_winner")
        submitted = st.form_submit_button("Guardar resultado", type="primary", width="stretch")
        if submitted:
            if table_snapshot(table_rows) != data.get("playoff_snapshot"):
                data["knockout"] = {}
                data["playoff_snapshot"] = table_snapshot(table_rows)
            data["knockout"][match_id] = {
                "home": home, "away": away, "home_goals": int(hg), "away_goals": int(ag),
                "advancing": advancing if hg == ag else (home if hg > ag else away),
            }
            save_data()
            st.rerun()


data = load_data()
table_rows = calculate_table()
page_options = ["Inicio", "Fechas y resultados", "Tabla de posiciones", "Eliminatorias", "Equipos"]

with st.sidebar:
    if ASSET_LOGO.exists():
        st.image(str(ASSET_LOGO), width="stretch")
    st.markdown("<div class='eyebrow'>Liga MJ · Temporada 1</div>", unsafe_allow_html=True)
    st.markdown("## Centro de competición")
    page = st.radio("Navegación", page_options, label_visibility="collapsed")
    st.markdown("---")
    played = len(completed_fixtures())
    st.markdown(f"**Partidos cargados**  \n{played}")
    st.caption("Los cambios se guardan automáticamente en liga_data.json")
    with st.expander("Respaldo de datos"):
        backup = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button("Descargar copia JSON", backup, file_name="liga_mj_backup.json", mime="application/json", width="stretch")
        uploaded_backup = st.file_uploader("Restaurar una copia JSON", type=["json"], key="backup_upload")
        if uploaded_backup is not None and st.button("Restaurar datos", key="restore_backup", type="primary"):
            try:
                restored = validate_backup(json.loads(uploaded_backup.getvalue().decode("utf-8")))
                data = restored
                save_data()
                st.success("Copia restaurada.")
                st.rerun()
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                st.error(f"No se pudo restaurar: {exc}")

if page == "Inicio":
    st.markdown('<div class="hero"><div class="eyebrow">Liga MJ · Temporada 1</div><div class="hero-title">EL CAMINO A LA GLORIA</div><p class="hero-sub">24 clubes · 3 presidentes · 8 fechas · un solo campeón.</p></div>', unsafe_allow_html=True)
    wins = [r for r in table_rows if r["Pts"] > 0]
    leader = table_rows[0]["team"] if wins else "—"
    completed_rounds = sum(bool(data["matchdays"][rid]["fixtures"]) and all(f.get("home_goals") is not None and f.get("away_goals") is not None for f in data["matchdays"][rid]["fixtures"]) for rid in ROUND_IDS)
    cols = st.columns(4)
    metrics = [("CLUBES", "24", "3 presidentes"), ("FECHAS COMPLETAS", str(completed_rounds), "de 8 programadas"), ("PARTIDOS JUGADOS", str(played), "resultados registrados"), ("LÍDER ACTUAL", leader, f"{table_rows[0]['Pts']} puntos" if wins else "La tabla empieza en cero")]
    for col, (label, value, hint) in zip(cols, metrics):
        col.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-hint">{hint}</div></div>', unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Así se define el campeonato</div>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        st.markdown('<div class="surface"><div class="owner-name">01 · Fase de liga</div><p>Arma las 8 fechas y carga los resultados. La clasificación se actualiza automáticamente.</p></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="surface"><div class="owner-name">02 · Eliminatorias</div><p>Los puestos 1–4 entran a cuartos. Del 5.º al 12.º disputan la fase previa.</p></div>', unsafe_allow_html=True)
    with c:
        st.markdown('<div class="surface"><div class="owner-name">03 · Descenso</div><p>Los puestos 23 y 24 al terminar las 8 fechas quedan marcados para descenso.</p></div>', unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Los tres presidentes</div>", unsafe_allow_html=True)
    owner_cols = st.columns(3)
    for col, (owner, roster) in zip(owner_cols, ROSTERS.items()):
        teams_html = "<br>".join(f"<span style='color:#5b6c7d'>0{n}</span> &nbsp;{team}" for n, team in enumerate(roster, 1))
        col.markdown(f'<div class="owner-card"><div class="owner-name">{owner} · 8 clubes</div><div class="owner-list">{teams_html}</div></div>', unsafe_allow_html=True)
    st.markdown("<div class='footer'>Liga MJ · Panel de administración y seguimiento · Temporada 1</div>", unsafe_allow_html=True)

elif page == "Fechas y resultados":
    st.markdown('<div class="eyebrow">Calendario oficial</div>', unsafe_allow_html=True)
    st.title("Fechas y resultados")
    st.caption("Organiza manualmente cada fecha. En una fecha, un club solo puede aparecer una vez.")
    rid = st.selectbox("Selecciona una fecha", ROUND_IDS, format_func=lambda x: data["matchdays"][x]["title"], key="selected_round")
    matchday = data["matchdays"][rid]
    with st.expander("Editar nombre de la fecha", expanded=False):
        with st.form(f"title_{rid}"):
            new_title = st.text_input("Nombre", value=matchday.get("title", f"Fecha {rid}"))
            if st.form_submit_button("Guardar nombre"):
                matchday["title"] = new_title.strip() or f"Fecha {rid}"
                save_data(); st.rerun()
    used = {team for fixture in matchday["fixtures"] for team in (fixture["home"], fixture["away"])}
    available = [team for team in TEAMS if team not in used]
    st.markdown("### Agregar partido")
    if len(available) < 2:
        st.info("Ya no quedan dos clubes libres en esta fecha.")
    else:
        with st.form(f"add_fixture_{rid}", clear_on_submit=True):
            x, y, z = st.columns([2, 2, 1])
            home = x.selectbox("Local", available, key=f"add_home_{rid}")
            away_choices = [team for team in available if team != home]
            away = y.selectbox("Visitante", away_choices, key=f"add_away_{rid}")
            submit_add = z.form_submit_button("＋ Agregar", type="primary", width="stretch")
            if submit_add:
                matchday["fixtures"].append({"id": uuid.uuid4().hex[:10], "home": home, "away": away, "home_goals": None, "away_goals": None})
                save_data(); st.rerun()

    st.markdown(f"### {matchday.get('title', f'Fecha {rid}')} <span class='pill pill-cyan'>{len(matchday['fixtures'])} PARTIDOS</span>", unsafe_allow_html=True)
    if not matchday["fixtures"]:
        st.markdown('<div class="surface">Todavía no hay partidos en esta fecha. Usa el formulario para armarla.</div>', unsafe_allow_html=True)
    for i, fixture in enumerate(list(matchday["fixtures"])):
        played_match = fixture.get("home_goals") is not None and fixture.get("away_goals") is not None
        with st.container(border=True):
            left, center, right = st.columns([4, 2, 4])
            left.markdown(f"**{fixture['home']}**  \n<small>{TEAM_OWNER[fixture['home']]}</small>", unsafe_allow_html=True)
            if played_match:
                center.markdown(f"<div style='text-align:center;color:#08d9e8;font-size:1.4rem;font-weight:800;padding-top:5px'>{fixture['home_goals']} : {fixture['away_goals']}</div>", unsafe_allow_html=True)
            else:
                center.markdown("<div style='text-align:center;color:#718295;padding-top:10px'>VS</div>", unsafe_allow_html=True)
            right.markdown(f"**{fixture['away']}**  \n<small>{TEAM_OWNER[fixture['away']]}</small>", unsafe_allow_html=True)
            with st.form(f"result_{rid}_{fixture['id']}"):
                h, a, save, delete = st.columns([1, 1, 2, 1])
                hg = h.number_input("Goles local", min_value=0, step=1, value=int(fixture.get("home_goals") or 0), key=f"hg_{rid}_{fixture['id']}")
                ag = a.number_input("Goles visitante", min_value=0, step=1, value=int(fixture.get("away_goals") or 0), key=f"ag_{rid}_{fixture['id']}")
                submitted = save.form_submit_button("Guardar resultado", type="primary", width="stretch")
                remove = delete.form_submit_button("Eliminar")
                if submitted:
                    fixture["home_goals"], fixture["away_goals"] = int(hg), int(ag)
                    save_data(); st.rerun()
                if remove:
                    matchday["fixtures"] = [f for f in matchday["fixtures"] if f["id"] != fixture["id"]]
                    save_data(); st.rerun()

elif page == "Tabla de posiciones":
    st.markdown('<div class="eyebrow">Clasificación general · 24 clubes</div>', unsafe_allow_html=True)
    st.title("Tabla de posiciones")
    st.caption("Desempates: enfrentamiento directo (cuando igualan dos equipos) → diferencia de goles → menos goles en contra → más goles a favor.")
    st.markdown('<div class="surface"><span class="pill pill-cyan">1–4 CUARTOS</span><span class="pill pill-cyan">5–12 FASE PREVIA</span><span class="pill pill-red">23–24 DESCENSO</span></div>', unsafe_allow_html=True)
    table_df = pd.DataFrame(table_rows)[["Pos", "team", "PJ", "G", "E", "P", "GF", "GC", "DG", "Pts"]].rename(columns={"team": "Equipo"})
    st.dataframe(table_df, width="stretch", hide_index=True, height=760, column_config={
        "Pos": st.column_config.NumberColumn("Pos", width="small"),
        "Equipo": st.column_config.TextColumn("Equipo", width="medium"),
        "PJ": st.column_config.NumberColumn("PJ", help="Partidos jugados"),
        "G": st.column_config.NumberColumn("G", help="Ganados"),
        "E": st.column_config.NumberColumn("E", help="Empatados"),
        "P": st.column_config.NumberColumn("P", help="Perdidos"),
        "GF": st.column_config.NumberColumn("GF", help="Goles a favor"),
        "GC": st.column_config.NumberColumn("GC", help="Goles en contra"),
        "DG": st.column_config.NumberColumn("DG", help="Diferencia de goles"),
        "Pts": st.column_config.NumberColumn("Pts", help="3 por victoria, 1 por empate", format="%d ⭐"),
    })
    st.markdown("<div class='small-note'>Si tres o más clubes igualan en puntos, se calcula una mini-tabla entre los equipos empatados antes de aplicar los criterios generales. Si dos empatados no se enfrentaron o su duelo directo quedó igualado, se continúa con diferencia de goles.</div>", unsafe_allow_html=True)
    st.markdown("<div class='footer'>Los puestos se calculan únicamente con partidos que tienen resultado guardado.</div>", unsafe_allow_html=True)

elif page == "Eliminatorias":
    st.markdown('<div class="eyebrow">Fase final · camino al título</div>', unsafe_allow_html=True)
    st.title("Eliminatorias")
    st.caption("Cuadro fijo según posiciones finales. Si una serie termina empatada, indica qué equipo avanza.")
    if not playoff_ready():
        st.warning("Para habilitar el registro de resultados de eliminatorias, completa las 8 fechas: cada fecha debe tener partidos y todos deben tener resultado. El cuadro se puede consultar desde ahora.")
    current_snapshot = table_snapshot(table_rows)
    snapshot_ok = data.get("playoff_snapshot") in (None, current_snapshot)
    if not snapshot_ok:
        st.warning("La tabla cambió desde que se guardaron resultados de eliminatorias. Esos resultados quedan temporalmente en pausa; al guardar un resultado con la nueva tabla, se reiniciarán para evitar asignarlos a cruces incorrectos.")
    positions = {row["Pos"]: row["team"] for row in table_rows}
    seeds = {n: positions[n] for n in range(1, 13)}
    ko_editable = playoff_ready() and snapshot_ok
    st.markdown("### Fase previa · posiciones 5–12")
    cols = st.columns(2)
    prelim = [("p_5_12", "5.º vs 12.º", (seeds[5], seeds[12])), ("p_7_10", "7.º vs 10.º", (seeds[7], seeds[10])), ("p_6_11", "6.º vs 11.º", (seeds[6], seeds[11])), ("p_8_9", "8.º vs 9.º", (seeds[8], seeds[9]))]
    for index, (mid, label, pair) in enumerate(prelim):
        col = cols[index % 2]
        with col:
            render_match_card(mid, label, pair, editable=ko_editable)
    winners = {mid: match_winner(mid, pair) for mid, _, pair in prelim}
    st.markdown("### Cuartos de final")
    quarters = [
        ("qf_1", "Llave 1 · 1.º vs ganador 5/12", (seeds[1], winners["p_5_12"])),
        ("qf_3", "Llave 2 · 3.º vs ganador 7/10", (seeds[3], winners["p_7_10"])),
        ("qf_2", "Llave 3 · 2.º vs ganador 6/11", (seeds[2], winners["p_6_11"])),
        ("qf_4", "Llave 4 · 4.º vs ganador 8/9", (seeds[4], winners["p_8_9"])),
    ]
    cols = st.columns(2)
    for index, (mid, label, pair) in enumerate(quarters):
        col = cols[index % 2]
        with col:
            render_match_card(mid, label, pair, editable=ko_editable)
    q_winners = {mid: match_winner(mid, pair) for mid, _, pair in quarters}
    st.markdown("### Semifinales")
    semis = [("sf_a", "Semifinal A · Llave 1 vs Llave 2", (q_winners["qf_1"], q_winners["qf_3"])), ("sf_b", "Semifinal B · Llave 3 vs Llave 4", (q_winners["qf_2"], q_winners["qf_4"]))]
    c1, c2 = st.columns(2)
    for col, (mid, label, pair) in zip([c1, c2], semis):
        with col:
            render_match_card(mid, label, pair, editable=ko_editable)
    sf_winners = {mid: match_winner(mid, pair) for mid, _, pair in semis}
    st.markdown("### Gran final")
    render_match_card("final", "Final · Campeón de Liga MJ", (sf_winners["sf_a"], sf_winners["sf_b"]), editable=ko_editable)
    champion = match_winner("final", (sf_winners["sf_a"], sf_winners["sf_b"]))
    if champion:
        st.success(f"¡{champion} es el campeón de la Liga MJ!")

elif page == "Equipos":
    st.markdown('<div class="eyebrow">Clubes participantes</div>', unsafe_allow_html=True)
    st.title("Los 24 equipos")
    st.caption("Planteles organizados por presidente.")
    cols = st.columns(3)
    for col, (owner, roster) in zip(cols, ROSTERS.items()):
        with col:
            st.markdown(f'<div class="owner-card"><div class="owner-name">{owner} · {len(roster)} equipos</div><div class="owner-list">' + "<br>".join(f"{n:02d} &nbsp; {team}" for n, team in enumerate(roster, 1)) + "</div></div>", unsafe_allow_html=True)
    st.markdown("### Reglas de la competición")
    st.markdown("- **Puntuación:** victoria 3 puntos, empate 1, derrota 0.\n- **Desempate entre dos:** puntos del enfrentamiento directo; luego diferencia de goles, menos goles en contra y más goles a favor.\n- **Desempate de tres o más:** mini-tabla entre los equipos igualados y, si persiste, los criterios generales.\n- **Clasificación:** puestos 1–4 a cuartos; 5–12 a fase previa; 23–24 a descenso.")
    st.info("La app no carga escudos externos: utiliza el logo de la liga y nombres de equipos para que el repositorio funcione sin claves ni servicios adicionales.")
