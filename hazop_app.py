import streamlit as st
import json, re, io
from datetime import datetime
import pandas as pd
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, BaseDocTemplate, PageTemplate, Frame)
from reportlab.lib.enums import TA_CENTER

# ════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════
st.set_page_config(page_title="HAZOP AI Assistant", page_icon="🛡️",
                   layout="wide", initial_sidebar_state="expanded")

# ════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
*{box-sizing:border-box}
html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif!important;color:#f1f5f9!important}
.stApp{background:#060e1f!important}
/* SIDEBAR */
section[data-testid="stSidebar"]{background:#0a1525!important;border-right:2px solid #f97316!important}
section[data-testid="stSidebar"] *{color:#e2e8f0!important}
section[data-testid="stSidebar"] label{color:#fbbf24!important;font-weight:700!important;font-size:0.82rem!important}
section[data-testid="stSidebar"] .stSelectbox>div>div{background:#060e1f!important;color:#f1f5f9!important;border:1px solid #334155!important;border-radius:5px!important}
/* HEADINGS */
h1,h2,h3,h4{font-family:'IBM Plex Mono',monospace!important;color:#f97316!important}
p,li{color:#e2e8f0!important}
/* HERO */
.hero-banner{background:linear-gradient(135deg,#1a0800,#1e293b 60%,#0d1829);border:2px solid #f97316;border-radius:10px;padding:1.8rem 2.2rem;margin-bottom:1.5rem;position:relative;overflow:hidden}
.hero-banner::after{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,transparent,#f97316,#fbbf24,#f97316,transparent)}
.hero-title{font-family:'IBM Plex Mono',monospace;font-size:2rem;font-weight:700;color:#f97316!important;margin:0;letter-spacing:-1px}
.hero-sub{font-size:0.85rem;color:#94a3b8!important;margin-top:0.5rem;font-family:'IBM Plex Mono',monospace;letter-spacing:1.5px}
/* INPUT PANEL */
.input-panel{background:#0a1525;border:2px solid #1e3a5f;border-radius:10px;padding:1.5rem 1.8rem;margin-bottom:1.5rem}
.panel-title{font-family:'IBM Plex Mono',monospace;font-size:0.72rem;letter-spacing:2px;color:#f97316!important;text-transform:uppercase;border-bottom:1px solid #1e3a5f;padding-bottom:0.5rem;margin-bottom:1rem}
/* TEXTAREA */
.stTextArea label{color:#fbbf24!important;font-weight:700!important;font-size:0.88rem!important}
.stTextArea textarea{background:#060e1f!important;border:2px solid #1e3a5f!important;color:#f1f5f9!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.84rem!important;border-radius:8px!important;line-height:1.65!important}
.stTextArea textarea:focus{border-color:#f97316!important;box-shadow:0 0 0 3px rgba(249,115,22,0.2)!important}
.stTextArea textarea::placeholder{color:#2d4a6b!important}
/* BUTTONS */
.stButton>button{background:linear-gradient(135deg,#f97316,#ea580c)!important;color:#fff!important;border:none!important;border-radius:8px!important;font-family:'IBM Plex Mono',monospace!important;font-weight:700!important;letter-spacing:1.5px!important;padding:0.75rem 1.5rem!important;font-size:0.9rem!important;width:100%!important;transition:all 0.2s!important}
.stButton>button:hover{background:linear-gradient(135deg,#fb923c,#f97316)!important;box-shadow:0 6px 20px rgba(249,115,22,0.4)!important}
/* SELECTBOX */
.stSelectbox label{color:#fbbf24!important;font-weight:700!important}
.stSelectbox>div>div{background:#0a1525!important;color:#f1f5f9!important;border:1px solid #334155!important;border-radius:7px!important}
/* MULTISELECT */
.stMultiSelect label{color:#fbbf24!important;font-weight:700!important}
.stMultiSelect>div{background:#0a1525!important;border:1px solid #334155!important;border-radius:7px!important}
.stMultiSelect span{color:#f1f5f9!important}
/* TABS */
.stTabs [data-baseweb="tab-list"]{background:#0a1525!important;border-radius:8px!important;padding:5px!important;gap:4px!important;border:1px solid #1e3a5f!important}
.stTabs [data-baseweb="tab"]{font-family:'IBM Plex Mono',monospace!important;color:#64748b!important;font-size:0.82rem!important;background:transparent!important;border-radius:6px!important;padding:8px 18px!important}
.stTabs [aria-selected="true"]{color:#fff!important;background:#f97316!important}
/* METRICS */
.metric-card{background:#0a1525;border:2px solid #334155;border-radius:10px;padding:1.2rem;text-align:center}
.metric-num{font-family:'IBM Plex Mono',monospace;font-size:2.4rem;font-weight:700;color:#f97316!important}
.metric-label{font-size:0.72rem;color:#64748b!important;text-transform:uppercase;letter-spacing:1.5px;margin-top:4px}
/* INFO BOX */
.info-box{background:#0a1525;border:1.5px solid #f97316;border-radius:8px;padding:1rem 1.3rem;margin:0.6rem 0}
.section-header{font-family:'IBM Plex Mono',monospace;font-size:0.72rem;letter-spacing:2px;color:#f97316!important;text-transform:uppercase;border-bottom:1px solid rgba(249,115,22,0.4);padding-bottom:0.4rem;margin-bottom:0.8rem}
/* HAZOP TABLE */
.hazop-wrap{overflow-x:auto;border:2px solid #f97316;border-radius:10px;margin-top:0.5rem}
.hazop-tbl{width:100%;border-collapse:collapse;font-family:'IBM Plex Sans',sans-serif;font-size:0.8rem}
.hazop-tbl thead tr{background:#0f2744}
.hazop-tbl thead th{padding:13px 10px;text-align:center;border:2px solid #f97316!important;background:#071830!important}
.hazop-tbl tbody tr{border-bottom:1px solid #1e3a5f}
.hazop-tbl tbody tr:hover{background:#0f2744!important}
.hazop-tbl tbody td{padding:10px 10px;vertical-align:top;border:1px solid #1e3a5f;line-height:1.65}
/* DOWNLOAD BUTTONS */
[data-testid="stDownloadButton"] button{background:#0a1525!important;color:#f97316!important;border:2px solid #f97316!important;border-radius:8px!important;font-family:'IBM Plex Mono',monospace!important;font-weight:700!important;letter-spacing:1px!important}
[data-testid="stDownloadButton"] button:hover{background:#f97316!important;color:#fff!important}
/* ALERTS */
div[data-testid="stAlert"]{background:#0a1525!important;border:1px solid #f97316!important;color:#f1f5f9!important;border-radius:8px!important}
/* EMPTY STATE */
.empty-state{text-align:center;padding:4rem 1rem;background:#0a1525;border-radius:12px;border:2px dashed #1e3a5f;margin-top:1rem}
.empty-state-icon{font-size:4rem;margin-bottom:1rem}
.empty-state-text{font-family:'IBM Plex Mono',monospace;font-size:1rem;color:#334155!important;letter-spacing:1px}
.empty-state-sub{font-size:0.85rem;color:#1e3a5f!important;margin-top:0.5rem}
/* STICKY FOOTER */
.sticky-footer{position:fixed;bottom:0;left:0;right:0;z-index:9999;background:linear-gradient(90deg,#0a1525,#1a0800,#0a1525);border-top:2px solid #f97316;padding:0.6rem 2rem;display:flex;align-items:center;justify-content:space-between}
footer{display:none!important}
#MainMenu{visibility:hidden!important}
.block-container{padding-bottom:4.5rem!important}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════════
RISK_EMOJI = {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡","LOW":"🟢"}
RISK_COLOR = {"CRITICAL":"#ef4444","HIGH":"#f97316","MEDIUM":"#eab308","LOW":"#22c55e"}
RISK_BG    = {"CRITICAL":"rgba(239,68,68,0.15)","HIGH":"rgba(249,115,22,0.12)",
              "MEDIUM":"rgba(234,179,8,0.1)","LOW":"rgba(34,197,94,0.08)"}
GW_COLOR   = {"NO":"#ef4444","MORE":"#f97316","LESS":"#3b82f6","REVERSE":"#a855f7",
              "OTHER THAN":"#ec4899","AS WELL AS":"#06b6d4","PART OF":"#84cc16"}

# ════════════════════════════════════════════════════════════════
# INDUSTRY → EQUIPMENT DATABASE
# ════════════════════════════════════════════════════════════════
INDUSTRIES = {
    "Oil & Gas": {
        "Centrifugal Pump (Crude Transfer)":
            "Centrifugal pump P-101 transferring crude oil (API 35, viscosity 15 cP) from storage tank TK-101 to crude distillation unit. Flow rate: 500 m³/hr, suction pressure: 2.5 bar, discharge pressure: 8 bar. Motor: 250 kW, mechanical seal, double isolation valve. Operating temperature: 60°C. Relief valve PSV-101 set at 10 bar.",
        "Reciprocating Compressor (Gas Injection)":
            "Reciprocating compressor K-201 for natural gas injection into reservoir. Suction pressure: 30 bar, discharge pressure: 350 bar, flow: 50,000 Sm³/day. Gas composition: 85% methane, 10% ethane, 5% CO2. Inter-stage coolers present. Vibration monitoring installed. Motor: 2.5 MW.",
        "3-Phase Separator (Well Test)":
            "Horizontal 3-phase separator V-301 separating well test fluids into gas, oil, and water. Operating at 45 bar, 80°C. Gas capacity: 1 MMSCFD, liquid: 5000 bbl/day. Level controls on oil and water outlets. High-pressure trip at 50 bar. H2S present at 200 ppm.",
        "Fired Heater (Crude Preheat)":
            "Fired heater F-101 preheating crude oil from 100°C to 300°C before atmospheric distillation. Fuel gas fired, thermal duty: 20 MW. Coil inlet pressure: 6 bar. Tube skin temperature max: 380°C. Excess O2 control, flame detector, BMS installed.",
        "Atmospheric Storage Tank (Crude)":
            "Floating roof storage tank TK-201, capacity 50,000 m³, storing crude oil at ambient temperature. Fixed foam system for fire protection. Level gauging: radar + manual. Dyke wall capacity: 110%. Nitrogen blanketing not used. API 650 design.",
        "Gas Scrubber (H2S Removal)":
            "Vertical gas scrubber V-401 removing H2S from sour gas using amine (MDEA) solvent. Gas inlet: 5 MMSCFD, 60 bar, 50°C. H2S inlet: 2%. Target outlet: <4 ppm H2S. Pressure differential control. Rich amine pumps P-401A/B.",
        "Control Valve (Flow Regulation)":
            "Control valve FCV-101 on crude oil transfer line. Cv = 120, line size 10 inch, pressure drop: 2 bar at normal flow. Globe valve, fail-closed actuator, positioner installed. Upstream isolation valve, bypass provided.",
    },
    "Petrochemical": {
        "CSTR Reactor (Polymerization)":
            "CSTR reactor R-101 for continuous polymerization of ethylene at 80°C, 15 bar. Feed: 2000 kg/hr ethylene monomer + catalyst slurry. Jacket cooling with chilled water at 10°C, cooling duty: 3 MW. Agitator: 200 kW. High-temperature trip at 95°C. Relief valve at 20 bar. Nitrogen padding.",
        "Distillation Column (Benzene/Toluene)":
            "Atmospheric distillation column T-101 separating benzene/toluene mixture. Feed: 10,000 kg/hr, 50% benzene at 120°C, 1.2 bar. 45 sieve trays. Overhead condenser E-101 (shell & tube), reboiler E-102 (kettle). Reflux ratio: 3.0. Overhead product: 99.9% benzene. Pressure control on overhead accumulator.",
        "Ethylene Oxide Reactor (Fixed Bed)":
            "Fixed bed catalytic reactor R-201 for ethylene oxidation to ethylene oxide. Feed: ethylene + O2 + diluent, inlet: 250°C, 20 bar. Highly exothermic. Multi-tube design, shell-side cooling. Temperature excursion trip at 280°C. O2 analyser on feed. Emergency quench system.",
        "Plate Heat Exchanger (Product Cooling)":
            "Plate heat exchanger E-301 cooling styrene monomer from 130°C to 40°C using cooling water. Area: 200 m². Hot side pressure: 4 bar, cold side: 3 bar. Inhibitor (TBC) dosing on styrene side to prevent polymerization. Differential pressure alarm on plates.",
        "Styrene Storage Tank (Pressurized)":
            "Pressurized storage tank TK-301 storing liquid styrene monomer at 20°C, 1.1 bar (N2 blanket). Capacity: 500 m³. Inhibitor monitoring system. Chilled water jacket to prevent polymerization. High-temperature alarm at 35°C. Grounding and bonding. Foam system.",
        "Scrubber Absorber (Caustic Wash)":
            "Packed tower absorber V-501 washing chlorine from reactor off-gas using 15% NaOH solution. Gas inlet: 2000 Nm³/hr, 40°C, 1.05 bar. NaOH recirculation pump P-501. Level control on sump. pH analyser on outlet liquor. Caustic dosing pump.",
        "Fin Fan Cooler (Naphtha)":
            "Air-cooled fin fan cooler E-201 cooling naphtha from 180°C to 60°C. Tube-side flow: 30,000 kg/hr at 6 bar. 3 bays, motor-driven fans with auto-variable pitch. High outlet temperature alarm. Located downwind of process units. Anti-freeze consideration for winter operation.",
    },
    "Pharmaceuticals": {
        "Batch Reactor (API Synthesis)":
            "Glass-lined batch reactor R-101, 5000 L capacity, for active pharmaceutical ingredient synthesis. Operating at 60°C, atmospheric pressure, solvent: dichloromethane (DCM). Jacket heating/cooling with thermal fluid. Nitrogen blanket maintained. Agitator seal: double mechanical. Solvent recovery condenser E-101.",
        "Centrifuge (Product Isolation)":
            "Disc centrifuge CF-101 separating API crystals from mother liquor. Feed slurry: 1000 L/batch, solvent: isopropanol (IPA). Rated speed: 3500 RPM. Explosion-proof motor. Inert gas purge before opening. Anti-static bonding. CIP system integrated.",
        "Solvent Recovery Column (IPA)":
            "Batch distillation column T-101 recovering isopropanol solvent, capacity 2000 L. Operating at atmospheric pressure, 82°C overhead. Direct steam injection reboiler. Overhead condenser E-101. High-level alarm on still pot. Nitrogen atmosphere. Water content analyser on distillate.",
        "Sterile Filtration Unit":
            "0.22 μm sterile filter housing F-101 for final product filtration before fill-finish. Stainless steel 316L housing, rated for 6 bar. Integrity test before each use. Differential pressure monitoring. Product contact surfaces: electropolished. No bypass line. Single use filter cartridges.",
        "Autoclave / Sterilizer":
            "Steam sterilization autoclave AC-101, 1500 L chamber, operating at 134°C, 3 bar steam. Double door design for clean/dirty separation. F0 value monitoring. Chamber drain with condensate cooler. Safety interlock prevents door opening under pressure. Calibrated temperature probes x3.",
        "Spray Dryer (Powder Production)":
            "Spray dryer SD-101 converting API solution to powder. Inlet temperature: 180°C, outlet: 80°C, feed rate: 50 kg/hr. Nitrogen closed-loop system (solvent-based product). Oxygen analyser: trip at >2% O2. Explosion vent panel on chamber. Powder collection cyclone + bag filter.",
    },
    "Power Generation": {
        "Boiler (High Pressure Steam)":
            "Water tube boiler B-101 generating steam at 100 bar, 540°C, capacity 200 T/hr. Fuel: natural gas. BMS with flame detectors. Safety valves: 2 nos, set at 110 bar. Feed water system: economizer + deaerator. Drum level: 3-element control. Emergency shutdown on low drum level.",
        "Steam Turbine (500 MW)":
            "Steam turbine TG-101, 500 MW output. HP/IP/LP sections. Inlet: 100 bar, 540°C. Exhaust to condenser at 0.05 bar. Overspeed trip at 110% rated speed. Thrust bearing monitoring. Lube oil system: main pump + emergency DC pump. Turning gear for cool-down.",
        "Gas Turbine (Combined Cycle)":
            "Gas turbine GT-201, 150 MW. Natural gas fuel at 35 bar. Inlet air: 600 kg/s. TIT: 1300°C. Combustion can design. Vibration monitoring on all bearings. Emergency fuel shut-off valve with 2-second closure. Fire and gas detection in turbine enclosure.",
        "Cooling Tower (Condenser Service)":
            "Induced draft cooling tower CT-101, capacity 50,000 m³/hr circulation. Cooling range: 42°C to 28°C. Drift eliminators installed. Chemical dosing: anti-scale, biocide, corrosion inhibitor. Basin level control. Fan motors: 12 × 200 kW. Legionella monitoring program.",
        "Transformer (Main Grid)":
            "Power transformer TR-101, 500 MVA, 400/220 kV, oil-cooled (ONAN/ONAF). Buchholz relay, winding temperature indicator, oil level indicator. Fire protection: deluge system, oil containment pit. Pressure relief device. Online DGA monitoring for dissolved gas analysis.",
        "Condenser (Steam Turbine)":
            "Surface condenser C-101 for steam turbine exhaust, surface area: 15,000 m². Shell-side: steam at 0.05 bar, 33°C. Tube-side: cooling water at 22°C inlet. Hotwell level control feeds boiler feed pumps. Air ejectors maintain vacuum. Leak detection by conductivity measurement.",
    },
    "Water Treatment": {
        "Chlorination System":
            "Chlorine dosing system DS-101 for potable water disinfection. Chlorine gas cylinders, 68 kg each. Vacuum regulator at cylinder, injector at pipe. Target residual: 0.5 mg/L. Gas detector in chlorine room (alarm at 0.5 ppm, trip at 1 ppm). Scrubber for emergency release. PPE station at entry.",
        "Sand Filtration Unit":
            "Gravity sand filter SF-101 treating surface water, flow: 5000 m³/hr per unit (4 units). Filter media: sand + anthracite, depth 900 mm. Differential pressure: 0.5 bar max before backwash. Backwash: 3 m/min for 10 min. Turbidity analyser on outlet. Underdrain system.",
        "Reverse Osmosis System":
            "RO membrane system RO-101 for desalination, capacity 1000 m³/day. Feed: 35,000 ppm TDS, product: <500 ppm. Operating pressure: 60 bar. High pressure pump P-101: 200 kW. Energy recovery device (ERD). Chemical dosing: antiscalant, acid. CIP system. Pressure vessels: 8-inch diameter.",
        "Sludge Dewatering (Belt Press)":
            "Belt filter press BFP-101 dewatering water treatment sludge. Feed: 4% DS, product: 25% DS cake. Belt wash water: 3 bar. Polymer dosing for conditioning. Belt tension: 4 bar. Speed: 2-5 m/min variable. Nip rollers: 12 stages. Sludge storage hopper: 50 m³.",
        "UV Disinfection System":
            "UV disinfection system UV-101, capacity 10,000 m³/hr, 254 nm wavelength. UV dose: 40 mJ/cm². Flow-through reactor, 36 UV lamps per module. Ballast failure alarm per lamp. Transmittance monitoring. Automatic wiper system for quartz sleeves. Validated per UVDGM.",
        "Chemical Dosing (Coagulant)":
            "Ferric sulfate coagulant dosing system DS-201. Storage tank: 20 m³, concentration: 40%. Metering pumps P-201A/B (duty/standby). Dose rate: 5-50 mg/L. pH monitoring downstream. Containment bund: 110%. Safety: eye wash, PPE, ventilation.",
    },
    "Food & Beverage": {
        "Pasteurization Unit (HTST)":
            "High temperature short time pasteurizer P-101 for milk processing. Flow: 20,000 L/hr. Heating section: 72°C for 15 seconds. Regeneration: 75% heat recovery. Flow diversion valve (FDV) diverts sub-pasteurized product back to raw side. Product/CIP interlock. Forward flow pump.",
        "CIP System (Clean-in-Place)":
            "CIP system serving processing vessels, tanks, pipelines. Circuits: 4 off. Chemicals: 2% NaOH at 80°C, 1.5% HNO3 at 70°C, final water rinse. Concentration analysers on both chemical tanks. Temperature monitoring. Flow verification per circuit. Chemical dosing: automatic.",
        "Spray Dryer (Milk Powder)":
            "Spray dryer SD-201 for whole milk powder. Inlet temperature: 200°C, outlet: 90°C. Evaporation rate: 3000 kg water/hr. Powder recovery: cyclone + bag filter. Explosion suppression on dryer chamber. CO detector in outlet duct. Fines return to nozzle chamber.",
        "Fermentation Tank (Beer)":
            "Cylindroconical fermentation vessel FV-101, 1000 hL capacity, stainless steel 316L. Operating temperature: 12°C (lager). Jacket cooling with glycol. CO2 pressure: 0.5 bar. Pressure relief: 0.8 bar. CIP connections. In-tank temperature probes ×4. CO2 recovery system.",
        "Homogenizer (Dairy)":
            "Two-stage homogenizer HM-101, capacity 30,000 L/hr at 180 bar first stage, 30 bar second stage. Product: whole milk. Plunger pump design. Pressure relief valve on each stage. High-pressure trip: 220 bar. Product temperature: max 75°C. Stainless steel product contact.",
        "Evaporator (Juice Concentration)":
            "Falling film evaporator EV-101, triple effect, capacity 10,000 kg water/hr. Product: fruit juice, 12 Brix to 65 Brix. Heating steam: 120°C first effect. Vacuum: 0.15 bar in third effect. CIP after each product change. Non-condensable gas venting. Aroma recovery column.",
    },
    "Steel & Metals": {
        "Blast Furnace (Iron Making)":
            "Blast furnace BF-101, volume 2500 m³, daily production 5000 T hot metal. Hot blast: 1200°C, 4.5 bar via stoves. Cooling water: 3000 m³/hr to tuyeres and hearth. Top gas pressure: 2.8 bar. Top gas recovery for fuel. Casthouse: 4 tapholes, 2 iron runners. CO gas monitoring throughout.",
        "Basic Oxygen Furnace (Steelmaking)":
            "BOF converter CV-101, capacity 300 T per heat. Oxygen blowing at 50,000 Nm³/hr via lance. Heat duration: 40 min. Hood gas cleaning: wet scrubber. Off-gas: CO rich, recovered to gas network. Temperature measurement: sub-lance. High-speed tapping with slag retention.",
        "Continuous Caster":
            "Continuous casting machine CC-101, 2-strand slab caster, slab size 250×1600 mm. Casting speed: 1.5 m/min. Mould cooling: 350 m³/hr demineralized water. Spray cooling: 8 zones. Break-out detection: thermocouple matrix in mould. Tundish heating: plasma torches.",
        "Rolling Mill (Hot Strip)":
            "Hot strip mill HSM-101, roughing + 7-stand finishing mill. Entry temperature: 1150°C, exit: 850°C. Roll force: max 40,000 kN per stand. Work roll cooling water: 12,000 m³/hr. Strip thickness control: X-ray gauge. Cobble detection: laser sensors. Emergency crop shear.",
        "Ladle Furnace (Secondary Metallurgy)":
            "Ladle furnace LF-101, capacity 300 T steel. Heating by 3-phase AC arc electrodes, 60 MVA. Argon stirring from bottom porous plugs. Alloy additions via conveyor. Temperature: 1580-1620°C. Fume extraction: 100,000 Nm³/hr. Electrode position control. Ladle car positioning.",
    },
    "Cement": {
        "Rotary Kiln (Clinker Production)":
            "Rotary kiln K-101, 75 m length, 5.2 m diameter, capacity 5000 T/day clinker. Kiln temperature: 1450°C in burning zone. Fuel: coal + petcoke, 80 T/hr total. Preheater: 5-stage cyclone. Shell temperature monitoring: scanner. Refractory thickness: 250 mm. Main drive: 3×800 kW.",
        "Raw Mill (Vertical Roller)":
            "Vertical roller mill VRM-101 grinding raw meal, capacity 400 T/hr. Roller pressure: 800 kN each (4 rollers). Table speed: 25 RPM. Separator: dynamic, cut size 90 μm. Mill inlet temperature: 280°C (hot gas). Explosion protection: CO measurement, inert gas injection.",
        "Cement Mill (Ball Mill)":
            "Closed circuit ball mill BM-101, capacity 150 T/hr OPC. Mill diameter: 4.6 m, length: 14 m. Mill feed: clinker + gypsum + limestone. Mill exit temperature: max 120°C. Separator: high efficiency. Water injection for cooling. Main drive: 3500 kW. Noise enclosure.",
        "Preheater Tower (Cyclone)":
            "5-stage cyclone preheater tower PH-101, height 120 m. Raw meal inlet: 350 T/hr. Gas flow: 350,000 Nm³/hr at 900°C from kiln. Calciner with separate combustion chamber. Cyclone efficiency: >95% per stage. Blockage detection: pressure differential. Bypass for high alkali control.",
        "Coal Mill (Fuel Preparation)":
            "Vertical roller mill CM-101 grinding coal/petcoke, capacity 50 T/hr. Product fineness: 15% on 90 μm. Inert atmosphere: CO2 injection. CO analyser with alarm and trip. Mill inlet gas temperature: 250°C max. Grounding on all rotating parts. Fire extinguishing: CO2 flooding.",
    },
    "Fertilizers": {
        "Ammonia Synthesis Reactor":
            "Multi-bed ammonia synthesis converter R-101, operating at 450°C, 150 bar. Feed: N2/H2 in 1:3 ratio, 50,000 Nm³/hr. Catalyst: iron-based, 150 m³. Inter-bed quench cooling. Converter inlet/outlet temperature control. Emergency depressurization to flare. High-temperature trip at 480°C.",
        "Urea Reactor (HP Section)":
            "Urea synthesis reactor R-201 at 183°C, 155 bar. Feed: liquid ammonia + CO2. Residence time: 30 min. Materials: 316L SS + titanium. Ammonia/CO2 ratio: 4:1. Carbamate corrosion monitoring. Relief valve to HP scrubber. Emergency CO2 trip valve.",
        "Ammonia Storage (Refrigerated)":
            "Refrigerated ammonia storage tank TK-101, capacity 20,000 T at -33°C, 1 bar. Double wall design. Refrigeration: 2×500 kW screw compressors. Pressure control: refrigeration + pressure relief + flare. Water curtain around tank. Gas detectors: 16 fixed points. Emergency shutdown: deluge activation.",
        "Nitric Acid Absorber":
            "Absorption tower AB-101 producing 60% nitric acid from NOx gases. Tower height: 30 m, 40 sieve trays. Gas inlet: tail gas + air, 1.5 bar, 60°C. Cooling water on trays. Platinum gauze catalyst in burner upstream. NOx tail gas analyser. Acid cooler: titanium tubes.",
        "Granulator (NPK Production)":
            "Drum granulator GR-101 producing NPK fertilizer, capacity 1500 T/day. Drum: 4 m dia × 10 m length. Steam injection + liquid phase from slurry. Product temperature: 75°C. Dust control: wet scrubber. Material buildup detection. Emergency water spray. Product screen + crusher.",
        "Prilling Tower (Urea)":
            "Urea prilling tower PT-101, height 65 m, capacity 2000 T/day. Urea melt at 140°C pumped to prilling bucket on top. Air draft: 2.5 m/s upward. Product: 2-4 mm spherical prills. Dust scrubber at base. Melt pump: heated jacketed. Anti-caking agent coating at base.",
    },
    "Pulp & Paper": {
        "Digester (Kraft Pulping)":
            "Continuous digester DG-101, capacity 1000 T/day air-dry pulp. Cooking temperature: 170°C, pressure: 8 bar. White liquor (NaOH + Na2S). H-factor control. Chip level radar. Liquor circulation pumps: 4×. Steam addition at multiple points. Digester discharge to blow tank at 1 bar.",
        "Recovery Boiler":
            "Recovery boiler RB-101, capacity 2500 T dry solids/day. Black liquor fired. Steam: 84 bar, 480°C, 220 T/hr. Smelt spout: 4 off, continuous smelt removal. Emergency water shut-off: smelt-water explosion prevention. Boiler water leak detection. Electrostatic precipitator for particulates.",
        "Bleaching Tower (ClO2)":
            "Chlorine dioxide bleaching tower BT-101, 4 stages D/E/D/E. Consistency: 10%. ClO2 generation on-site (Mathieson process). ClO2 scrubber for venting. Residual ClO2 analyser at each stage outlet. Emergency dilution water. Personal monitors for all operators. Confined space procedures.",
        "Paper Machine (Fourdrinier)":
            "Fourdrinier paper machine PM-101, width 9.6 m, speed 1500 m/min, capacity 800 T/day. Headbox pressure: 0.6 bar. Press section: 3 nips. Dryer section: 60 steam-heated cylinders. Steam: 6 bar, condensate return via syphons. Web break detection. Pope reel winding.",
        "Lime Kiln (Causticizing)":
            "Rotary lime kiln LK-101, 4 m dia × 80 m length, capacity 500 T/day lime. Fuel: non-condensable gases (NCGs) + fuel oil backup. Temperature: 1200°C. Lime mud feed: 70% solids. Ring formation monitoring. Dust scrubber. Shell temperature scanner. Combustion air fan: 200,000 Nm³/hr.",
    },
}

# ════════════════════════════════════════════════════════════════
# GROQ CLIENT
# ════════════════════════════════════════════════════════════════
@st.cache_resource
def get_client():
    key = st.secrets.get("GROQ_API_KEY","")
    if not key:
        st.error("❌ GROQ_API_KEY missing. Add it in Streamlit Secrets.")
        st.stop()
    return Groq(api_key=key)

SYSTEM_PROMPT = """You are a senior Process Safety Engineer (20+ years, IEC 61882).
Perform a thorough HAZOP study on the given process node.
Return ONLY valid JSON — no markdown, no explanation, nothing else.

{
  "node_name": "string",
  "process_intent": "string",
  "deviations": [
    {
      "guide_word": "NO|MORE|LESS|REVERSE|OTHER THAN|AS WELL AS|PART OF",
      "parameter": "Flow|Temperature|Pressure|Level|Composition|Speed|Viscosity|pH",
      "deviation": "concise deviation e.g. No Flow",
      "possible_causes": ["cause1","cause2","cause3"],
      "consequences": ["consequence1","consequence2"],
      "safeguards": ["safeguard1","safeguard2"],
      "recommendations": ["action1","action2"],
      "risk_level": "CRITICAL|HIGH|MEDIUM|LOW",
      "likelihood": "Rare|Unlikely|Possible|Likely|Almost Certain",
      "severity": "Minor|Moderate|Serious|Critical|Catastrophic"
    }
  ],
  "summary": {
    "critical_count":0,"high_count":0,"medium_count":0,"low_count":0,
    "top_recommendation":"string"
  }
}
Generate 10-14 meaningful deviations covering all major guide words and parameters.
Return ONLY the JSON object — no text before or after."""

def run_hazop(client, description, industry):
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":f"Industry: {industry}\nNode Description:\n{description}\n\nReturn JSON only."}
        ],
        temperature=0.3, max_tokens=4500
    )
    raw = re.sub(r"```json|```","",resp.choices[0].message.content.strip()).strip()
    return json.loads(raw)

# ════════════════════════════════════════════════════════════════
# PDF GENERATOR
# ════════════════════════════════════════════════════════════════
def generate_pdf(data, industry):
    buf = io.BytesIO()
    ORANGE = colors.HexColor("#f97316"); DARK = colors.HexColor("#0f172a")
    NAVY   = colors.HexColor("#0f2744"); SILVER = colors.HexColor("#e2e8f0")
    GOLD   = colors.HexColor("#fbbf24"); RED = colors.HexColor("#ef4444")
    GREEN  = colors.HexColor("#22c55e"); YELLOW = colors.HexColor("#eab308")
    WHITE  = colors.white; GRAY = colors.HexColor("#1e3a5f")
    RISK_PDF = {"CRITICAL":RED,"HIGH":ORANGE,"MEDIUM":YELLOW,"LOW":GREEN}

    now        = datetime.now().strftime("%B %d, %Y  %H:%M")
    summary    = data.get("summary",{})
    deviations = data.get("deviations",[])

    bs  = ParagraphStyle("b",fontName="Helvetica",fontSize=8,textColor=SILVER,leading=11)
    bos = ParagraphStyle("bo",fontName="Helvetica-Bold",fontSize=8,textColor=GOLD,leading=11)
    cs  = ParagraphStyle("c",fontName="Helvetica",fontSize=7.5,textColor=SILVER,leading=10)
    hs  = ParagraphStyle("h",fontName="Helvetica-Bold",fontSize=7.5,textColor=GOLD,leading=10)

    def draw_header(canvas, doc):
        """Drawn on every page — header only."""
        W,H = A4
        canvas.saveState()
        canvas.setFillColor(NAVY); canvas.rect(0,H-1.8*cm,W,1.8*cm,fill=1,stroke=0)
        canvas.setFillColor(ORANGE); canvas.rect(0,H-1.83*cm,W,0.07*cm,fill=1,stroke=0)
        canvas.setFillColor(ORANGE); canvas.setFont("Helvetica-Bold",11)
        canvas.drawString(1.5*cm,H-1.18*cm,"HAZOP STUDY REPORT")
        canvas.setFillColor(colors.HexColor("#94a3b8")); canvas.setFont("Helvetica",8)
        canvas.drawRightString(W-1.5*cm,H-1.18*cm,f"Node: {data.get('node_name','')}")
        canvas.setFont("Helvetica",7.5)
        canvas.drawString(1.5*cm,H-1.55*cm,f"IEC 61882  ·  {industry}  ·  Generated: {now}")
        canvas.restoreState()

    # Two-pass approach: first pass counts pages, second pass draws footer only on last page.
    class FooterOnLastPage:
        def __init__(self):
            self.total_pages = None

        def __call__(self, canvas, doc):
            draw_header(canvas, doc)
            if self.total_pages is not None and doc.page == self.total_pages:
                W,H = A4
                canvas.saveState()
                canvas.setFillColor(NAVY); canvas.rect(0,0,W,1.4*cm,fill=1,stroke=0)
                canvas.setFillColor(ORANGE); canvas.rect(0,1.4*cm,W,0.06*cm,fill=1,stroke=0)
                canvas.setFillColor(GREEN); canvas.setFont("Helvetica-Bold",8)
                canvas.drawString(1.5*cm,0.82*cm,"Developed by")
                canvas.setFillColor(WHITE); canvas.setFont("Helvetica-Bold",8)
                canvas.drawString(3.35*cm,0.82*cm,"Zunair Shahzad")
                canvas.setFillColor(GOLD); canvas.setFont("Helvetica",8)
                canvas.drawString(5.7*cm,0.82*cm,"· UET Lahore")
                canvas.setFillColor(WHITE); canvas.setFont("Helvetica",8)
                canvas.drawString(7.9*cm,0.82*cm,"(New Campus)")
                canvas.setFillColor(colors.HexColor("#475569")); canvas.setFont("Helvetica",7.5)
                canvas.drawString(1.5*cm,0.44*cm,"AI-Powered Engineering Series  ·  Not a substitute for certified HAZOP")
                canvas.setFillColor(colors.HexColor("#94a3b8")); canvas.setFont("Helvetica",8)
                canvas.drawRightString(W-1.5*cm,0.82*cm,f"Page {doc.page}")
                canvas.restoreState()

    footer_cb = FooterOnLastPage()

    frame    = Frame(1.5*cm,1.8*cm,A4[0]-3*cm,A4[1]-3.8*cm,id="main")
    template = PageTemplate(id="main",frames=[frame],onPage=footer_cb)
    doc2     = BaseDocTemplate(buf,pagesize=A4,pageTemplates=[template])
    story    = []

    story.append(Spacer(1,0.4*cm))
    story.append(Paragraph("HAZOP STUDY REPORT",
        ParagraphStyle("t",fontName="Helvetica-Bold",fontSize=18,textColor=ORANGE,alignment=TA_CENTER,spaceAfter=4)))
    story.append(Paragraph("Hazard and Operability Study  ·  AI-Assisted Analysis",
        ParagraphStyle("s",fontName="Helvetica",fontSize=9,textColor=colors.HexColor("#94a3b8"),alignment=TA_CENTER,spaceAfter=4)))
    story.append(Spacer(1,0.3*cm))

    info = [
        [Paragraph("<b>Node</b>",bos), Paragraph(data.get("node_name",""),bs),
         Paragraph("<b>Industry</b>",bos), Paragraph(industry,bs)],
        [Paragraph("<b>Date</b>",bos), Paragraph(now,bs),
         Paragraph("<b>Standard</b>",bos), Paragraph("IEC 61882",bs)],
        [Paragraph("<b>Intent</b>",bos), Paragraph(data.get("process_intent",""),bs),"",""],
    ]
    it = Table(info,colWidths=[2.8*cm,5.7*cm,2.8*cm,5.7*cm])
    it.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),DARK),("BACKGROUND",(0,0),(0,-1),NAVY),
        ("BACKGROUND",(2,0),(2,1),NAVY),
        ("BOX",(0,0),(-1,-1),1.5,ORANGE),("INNERGRID",(0,0),(-1,-1),0.5,GRAY),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),8),
        ("SPAN",(1,2),(3,2)),
    ]))
    story.append(it); story.append(Spacer(1,0.4*cm))

    story.append(Paragraph("RISK SUMMARY",
        ParagraphStyle("sh",fontName="Helvetica-Bold",fontSize=9,textColor=ORANGE,spaceAfter=4)))
    riskd = [
        [Paragraph("CRITICAL",ParagraphStyle("r",fontName="Helvetica-Bold",fontSize=8,textColor=RED)),
         Paragraph("HIGH",    ParagraphStyle("r",fontName="Helvetica-Bold",fontSize=8,textColor=ORANGE)),
         Paragraph("MEDIUM",  ParagraphStyle("r",fontName="Helvetica-Bold",fontSize=8,textColor=YELLOW)),
         Paragraph("LOW",     ParagraphStyle("r",fontName="Helvetica-Bold",fontSize=8,textColor=GREEN)),
         Paragraph("TOTAL",   ParagraphStyle("r",fontName="Helvetica-Bold",fontSize=8,textColor=GOLD))],
        [Paragraph(str(summary.get("critical_count",0)),ParagraphStyle("n",fontName="Helvetica-Bold",fontSize=16,textColor=RED,alignment=TA_CENTER)),
         Paragraph(str(summary.get("high_count",0)),    ParagraphStyle("n",fontName="Helvetica-Bold",fontSize=16,textColor=ORANGE,alignment=TA_CENTER)),
         Paragraph(str(summary.get("medium_count",0)),  ParagraphStyle("n",fontName="Helvetica-Bold",fontSize=16,textColor=YELLOW,alignment=TA_CENTER)),
         Paragraph(str(summary.get("low_count",0)),     ParagraphStyle("n",fontName="Helvetica-Bold",fontSize=16,textColor=GREEN,alignment=TA_CENTER)),
         Paragraph(str(len(deviations)),                ParagraphStyle("n",fontName="Helvetica-Bold",fontSize=16,textColor=GOLD,alignment=TA_CENTER))],
    ]
    rt = Table(riskd,colWidths=[3.4*cm]*5)
    rt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),DARK),("BOX",(0,0),(-1,-1),1.5,ORANGE),
        ("INNERGRID",(0,0),(-1,-1),0.5,GRAY),("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
    ]))
    story.append(rt)

    if summary.get("top_recommendation"):
        story.append(Spacer(1,0.3*cm))
        tt = Table([[Paragraph("⚠ TOP PRIORITY",ParagraphStyle("tp",fontName="Helvetica-Bold",fontSize=8,textColor=RED)),
                     Paragraph(summary.get("top_recommendation",""),bs)]],colWidths=[3.5*cm,13.5*cm])
        tt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#1a0000")),
            ("BOX",(0,0),(-1,-1),1.5,RED),("INNERGRID",(0,0),(-1,-1),0.5,colors.HexColor("#3f0000")),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),8),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),("LEFTPADDING",(0,0),(-1,-1),8),
        ]))
        story.append(tt)

    story.append(Spacer(1,0.5*cm))
    story.append(HRFlowable(width="100%",thickness=1.5,color=ORANGE))
    story.append(Spacer(1,0.3*cm))
    story.append(Paragraph("DETAILED HAZOP DEVIATION WORKSHEET",
        ParagraphStyle("sh2",fontName="Helvetica-Bold",fontSize=9,textColor=ORANGE,spaceAfter=6)))

    col_w = [0.5*cm,1.5*cm,1.7*cm,2.1*cm,3.0*cm,3.0*cm,2.7*cm,2.6*cm,1.9*cm]
    hdr   = [Paragraph(t,hs) for t in ["#","Guide Word","Parameter","Deviation",
             "Possible Causes","Consequences","Safeguards","Recommendations","Risk/Likelihood/Severity"]]
    tdata = [hdr]
    scmds = [
        ("BACKGROUND",(0,0),(-1,0),NAVY),
        ("BOX",(0,0),(-1,-1),1.5,ORANGE),("INNERGRID",(0,0),(-1,-1),0.5,GRAY),
        ("ALIGN",(0,0),(-1,0),"CENTER"),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[DARK,colors.HexColor("#0a1520")]),
    ]
    for i,dev in enumerate(deviations,1):
        risk  = dev.get("risk_level","LOW")
        rcol  = RISK_PDF.get(risk,GREEN)
        row = [
            Paragraph(str(i),ParagraphStyle("n",fontName="Helvetica",fontSize=7.5,textColor=colors.HexColor("#64748b"),alignment=TA_CENTER)),
            Paragraph(dev.get("guide_word",""),ParagraphStyle("gw",fontName="Helvetica-Bold",fontSize=7.5,textColor=ORANGE)),
            Paragraph(dev.get("parameter",""),cs),
            Paragraph(dev.get("deviation",""),ParagraphStyle("dv",fontName="Helvetica-Bold",fontSize=7.5,textColor=WHITE)),
            Paragraph("\n".join([f"- {c}" for c in dev.get("possible_causes",[])]),cs),
            Paragraph("\n".join([f"- {c}" for c in dev.get("consequences",[])]),ParagraphStyle("cq",fontName="Helvetica",fontSize=7.5,textColor=colors.HexColor("#fca5a5"),leading=10)),
            Paragraph("\n".join([f"- {s}" for s in dev.get("safeguards",[])]),ParagraphStyle("sg",fontName="Helvetica",fontSize=7.5,textColor=colors.HexColor("#86efac"),leading=10)),
            Paragraph("\n".join([f"- {r}" for r in dev.get("recommendations",[])]),ParagraphStyle("rc",fontName="Helvetica",fontSize=7.5,textColor=colors.HexColor("#fde68a"),leading=10)),
            Paragraph(f"{risk}\n{dev.get('likelihood','')}\n{dev.get('severity','')}",ParagraphStyle("rk",fontName="Helvetica-Bold",fontSize=7.5,textColor=rcol,alignment=TA_CENTER)),
        ]
        tdata.append(row)

    ht = Table(tdata,colWidths=col_w,repeatRows=1)
    ht.setStyle(TableStyle(scmds))
    story.append(ht)

    # First pass: build to a dummy buffer just to count pages
    import copy
    dummy_buf = io.BytesIO()
    dummy_frame    = Frame(1.5*cm,1.8*cm,A4[0]-3*cm,A4[1]-3.8*cm,id="main")
    dummy_template = PageTemplate(id="main",frames=[dummy_frame],onPage=lambda c,d: None)
    dummy_doc      = BaseDocTemplate(dummy_buf,pagesize=A4,pageTemplates=[dummy_template])
    dummy_doc.build(copy.deepcopy(story))
    footer_cb.total_pages = dummy_doc.page

    # Second pass: real build with footer on last page
    doc2.build(story)
    return buf.getvalue()

# ════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-banner">
  <div class="hero-title">🛡️ HAZOP AI ASSISTANT</div>
  <div class="hero-sub">// HAZARD &amp; OPERABILITY STUDY — IEC 61882 — POWERED BY GROQ LLAMA 3.3 //</div>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="panel-title">// Select Industry</div>', unsafe_allow_html=True)
    industry_list = list(INDUSTRIES.keys())
    sel_industry  = st.selectbox("Industry", industry_list, key="sel_industry")

    st.markdown('<div class="panel-title">// Select Equipment</div>', unsafe_allow_html=True)
    equip_list = list(INDUSTRIES[sel_industry].keys())
    sel_equip  = st.selectbox("Equipment", equip_list, key="sel_equip")

    if st.button("📋 Load into Input Box"):
        st.session_state["input_text"] = INDUSTRIES[sel_industry][sel_equip]
        st.session_state["loaded_industry"] = sel_industry
        st.success("✅ Loaded! Click 'RUN HAZOP' to analyze.")
        st.rerun()

    st.markdown("---")
    st.markdown('<div class="panel-title">// Risk Filter</div>', unsafe_allow_html=True)
    show_risk = st.multiselect("Show Risk Levels",
        ["CRITICAL","HIGH","MEDIUM","LOW"],
        default=["CRITICAL","HIGH","MEDIUM","LOW"])
    st.markdown("---")
    st.markdown("""<div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#475569;line-height:2.1">
    <span style="color:#f97316;font-weight:700">GUIDE WORDS:</span><br>
    NO · MORE · LESS · REVERSE<br>OTHER THAN · AS WELL AS · PART OF<br><br>
    <span style="color:#334155">IEC 61882 Compliant</span></div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# MAIN INPUT
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="input-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-title">// Process Node Input — Type Manually OR Load from Sidebar</div>', unsafe_allow_html=True)

# FIX: persist loaded text across reruns using session_state
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

node_input = st.text_area(
    "Process Node Description",
    value=st.session_state["input_text"],
    height=165,
    placeholder=(
        "Type or paste your process node description here...\n\n"
        "Example: Centrifugal pump P-101 transferring crude oil from storage tank TK-101.\n"
        "Flow rate: 500 m³/hr, discharge pressure: 8 bar, temperature: 60°C.\n"
        "Motor: 250 kW, mechanical seal. Relief valve PSV-101 set at 10 bar.\n\n"
        "OR use the sidebar to select Industry → Equipment → Load into Input Box"
    )
)
# Sync manual typing back to session state
st.session_state["input_text"] = node_input

industry_for_run = st.session_state.get("loaded_industry", sel_industry)

c1, c2, c3 = st.columns([2,1,2])
with c2:
    run_btn = st.button("▶  RUN HAZOP", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# RUN
# ════════════════════════════════════════════════════════════════
if run_btn:
    current_input = st.session_state.get("input_text","").strip()
    if not current_input:
        st.warning("⚠️ Please enter a process description or load one from the sidebar.")
    else:
        client = get_client()
        with st.spinner("🤖 AI conducting HAZOP study... (~15 seconds)"):
            try:
                data = run_hazop(client, current_input, industry_for_run)
                st.session_state["hazop_data"]   = data
                st.session_state["run_industry"] = industry_for_run
                st.success(f"✅ HAZOP complete — {len(data.get('deviations',[]))} deviations identified for **{data.get('node_name','')}**")
            except json.JSONDecodeError as e:
                st.error(f"❌ JSON parse error: {e}. Please try again.")
                st.stop()
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.stop()

# ════════════════════════════════════════════════════════════════
# RESULTS
# ════════════════════════════════════════════════════════════════
if "hazop_data" in st.session_state:
    data       = st.session_state["hazop_data"]
    summary    = data.get("summary",{})
    deviations = [d for d in data.get("deviations",[]) if d.get("risk_level","LOW") in show_risk]

    st.markdown("---")
    st.markdown(f"### 📍 Node: `{data.get('node_name','Process Node')}`")

    # METRICS
    m1,m2,m3,m4,m5 = st.columns(5)
    for col,num,label,color,bg in [
        (m1,len(deviations),                 "Deviations", "#f97316","rgba(249,115,22,0.15)"),
        (m2,summary.get("critical_count",0), "Critical",   "#ef4444","rgba(239,68,68,0.15)"),
        (m3,summary.get("high_count",0),     "High",       "#f97316","rgba(249,115,22,0.12)"),
        (m4,summary.get("medium_count",0),   "Medium",     "#eab308","rgba(234,179,8,0.1)"),
        (m5,summary.get("low_count",0),      "Low",        "#22c55e","rgba(34,197,94,0.1)"),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card" style="border-color:{color};background:{bg}">
                <div class="metric-num" style="color:{color}!important">{num}</div>
                <div class="metric-label">{label}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""<div class="info-box">
        <div class="section-header">Design Intent</div>
        <p style="color:#e2e8f0!important;font-size:0.93rem;margin:0">{data.get("process_intent","")}</p>
    </div>""", unsafe_allow_html=True)
    if summary.get("top_recommendation"):
        st.markdown(f"""<div class="info-box" style="border-color:#ef4444;background:rgba(239,68,68,0.08)">
            <div class="section-header" style="color:#ef4444!important;border-color:#ef4444!important">⚠ Top Priority Action</div>
            <p style="color:#fca5a5!important;font-size:0.93rem;margin:0">{summary.get("top_recommendation","")}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋  HAZOP WORKSHEET","📊  RISK MATRIX","💾  EXPORT"])

    # ── TAB 1: TABLE ─────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-header">// Formal HAZOP Deviation Worksheet — IEC 61882</div>', unsafe_allow_html=True)
        st.markdown('<div class="hazop-wrap"><table class="hazop-tbl">', unsafe_allow_html=True)
        # HEADER — white text, dark background, full borders
        st.markdown("""
        <thead><tr style="background:#071830!important">
          <th style="width:34px;padding:13px 6px;background:#071830!important;border:2px solid #f97316!important;text-align:center"><span style="color:#f97316;font-weight:900;font-size:0.8rem;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:1px">#</span></th>
          <th style="padding:13px 10px;background:#071830!important;border:2px solid #f97316!important;text-align:center"><span style="color:#f97316;font-weight:900;font-size:0.8rem;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:1px">Guide Word</span></th>
          <th style="padding:13px 10px;background:#071830!important;border:2px solid #f97316!important;text-align:center"><span style="color:#f97316;font-weight:900;font-size:0.8rem;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:1px">Parameter</span></th>
          <th style="padding:13px 10px;background:#071830!important;border:2px solid #f97316!important;text-align:center"><span style="color:#f97316;font-weight:900;font-size:0.8rem;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:1px">Deviation</span></th>
          <th style="padding:13px 10px;background:#071830!important;border:2px solid #f97316!important;text-align:center"><span style="color:#f97316;font-weight:900;font-size:0.8rem;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:1px">Possible Causes</span></th>
          <th style="padding:13px 10px;background:#071830!important;border:2px solid #f97316!important;text-align:center"><span style="color:#f97316;font-weight:900;font-size:0.8rem;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:1px">Consequences</span></th>
          <th style="padding:13px 10px;background:#071830!important;border:2px solid #f97316!important;text-align:center"><span style="color:#f97316;font-weight:900;font-size:0.8rem;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:1px">Safeguards</span></th>
          <th style="padding:13px 10px;background:#071830!important;border:2px solid #f97316!important;text-align:center"><span style="color:#f97316;font-weight:900;font-size:0.8rem;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:1px">Recommendations</span></th>
          <th style="padding:13px 10px;background:#071830!important;border:2px solid #f97316!important;text-align:center"><span style="color:#f97316;font-weight:900;font-size:0.8rem;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:1px">Likelihood</span></th>
          <th style="padding:13px 10px;background:#071830!important;border:2px solid #f97316!important;text-align:center"><span style="color:#f97316;font-weight:900;font-size:0.8rem;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:1px">Severity</span></th>
          <th style="padding:13px 10px;background:#071830!important;border:2px solid #f97316!important;text-align:center"><span style="color:#f97316;font-weight:900;font-size:0.8rem;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:1px">Risk Level</span></th>
        </tr></thead><tbody>
        """, unsafe_allow_html=True)

        for i, dev in enumerate(deviations):
            risk   = dev.get("risk_level","LOW")
            rcol   = RISK_COLOR.get(risk,"#64748b")
            rbg    = RISK_BG.get(risk,"transparent")
            gwcol  = GW_COLOR.get(dev.get("guide_word",""),"#94a3b8")
            row_bg = "#0a1525" if i%2==0 else "#071018"

            causes  = "<br>".join([f"<span style='color:#cbd5e1'>• {c}</span>" for c in dev.get("possible_causes",[])])
            conseqs = "<br>".join([f"<span style='color:#fca5a5'>⚡ {c}</span>" for c in dev.get("consequences",[])])
            safeg   = "<br>".join([f"<span style='color:#86efac'>✅ {s}</span>" for s in dev.get("safeguards",[])])
            recs    = "<br>".join([f"<span style='color:#fde68a'>🔧 {r}</span>" for r in dev.get("recommendations",[])])

            st.markdown(f"""
            <tr style="background:{row_bg}">
              <td style="text-align:center;color:#475569;font-weight:700;font-size:0.78rem;border:1px solid #1e3a5f">{i+1}</td>
              <td style="text-align:center;border:1px solid #1e3a5f">
                <span style="background:{gwcol}22;color:{gwcol};border:1px solid {gwcol};
                  border-radius:4px;padding:3px 7px;font-weight:700;font-size:0.72rem;
                  white-space:nowrap;font-family:'IBM Plex Mono',monospace">{dev.get('guide_word','')}</span>
              </td>
              <td style="text-align:center;color:#94a3b8;font-weight:600;white-space:nowrap;font-size:0.79rem;border:1px solid #1e3a5f">{dev.get('parameter','')}</td>
              <td style="color:#ffffff;font-weight:700;font-size:0.82rem;min-width:130px;border:1px solid #1e3a5f">{dev.get('deviation','')}</td>
              <td style="min-width:150px;font-size:0.79rem;border:1px solid #1e3a5f">{causes}</td>
              <td style="min-width:150px;font-size:0.79rem;border:1px solid #1e3a5f">{conseqs}</td>
              <td style="min-width:145px;font-size:0.79rem;border:1px solid #1e3a5f">{safeg}</td>
              <td style="min-width:150px;font-size:0.79rem;border:1px solid #1e3a5f">{recs}</td>
              <td style="text-align:center;color:#94a3b8;white-space:nowrap;font-size:0.78rem;border:1px solid #1e3a5f">{dev.get('likelihood','')}</td>
              <td style="text-align:center;color:#e2e8f0;white-space:nowrap;font-size:0.78rem;border:1px solid #1e3a5f">{dev.get('severity','')}</td>
              <td style="text-align:center;background:{rbg};min-width:88px;border:1px solid #1e3a5f">
                <span style="color:{rcol};font-weight:700;font-family:'IBM Plex Mono',monospace;font-size:0.78rem">
                  {RISK_EMOJI.get(risk,'')} {risk}</span></td>
            </tr>""", unsafe_allow_html=True)

        st.markdown("</tbody></table></div>", unsafe_allow_html=True)

    # ── TAB 2: RISK MATRIX ────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">// Risk Distribution</div>', unsafe_allow_html=True)
        rc = {"CRITICAL":0,"HIGH":0,"MEDIUM":0,"LOW":0}
        for d in data.get("deviations",[]):
            r=d.get("risk_level","LOW")
            if r in rc: rc[r]+=1
        st.bar_chart(pd.DataFrame({"Count":rc}).rename_axis("Risk Level"),color="#f97316")
        st.markdown('<div class="section-header">// Summary Table</div>', unsafe_allow_html=True)
        rows = [{"#":i+1,"Guide Word":d.get("guide_word",""),"Parameter":d.get("parameter",""),
                 "Deviation":d.get("deviation",""),"Risk":d.get("risk_level",""),
                 "Likelihood":d.get("likelihood",""),"Severity":d.get("severity","")}
                for i,d in enumerate(data.get("deviations",[]))]
        if rows:
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    # ── TAB 3: EXPORT ─────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">// Export Options</div>', unsafe_allow_html=True)
        e1,e2,e3 = st.columns(3)
        with e1:
            pdf_b = generate_pdf(data, st.session_state.get("run_industry","General"))
            st.download_button("⬇️ PDF Report (Professional)",
                data=pdf_b,
                file_name=f"HAZOP_{data.get('node_name','report').replace(' ','_')}.pdf",
                mime="application/pdf",use_container_width=True)
        with e2:
            csv_rows = [{"Node":data.get("node_name",""),"Guide Word":d.get("guide_word",""),
                "Parameter":d.get("parameter",""),"Deviation":d.get("deviation",""),
                "Causes":" | ".join(d.get("possible_causes",[])),
                "Consequences":" | ".join(d.get("consequences",[])),
                "Safeguards":" | ".join(d.get("safeguards",[])),
                "Recommendations":" | ".join(d.get("recommendations",[])),
                "Risk":d.get("risk_level",""),"Likelihood":d.get("likelihood",""),
                "Severity":d.get("severity","")} for d in data.get("deviations",[])]
            st.download_button("⬇️ CSV Worksheet",
                data=pd.DataFrame(csv_rows).to_csv(index=False),
                file_name=f"HAZOP_{data.get('node_name','report').replace(' ','_')}.csv",
                mime="text/csv",use_container_width=True)
        with e3:
            st.download_button("⬇️ JSON Data",
                data=json.dumps(data,indent=2),
                file_name=f"HAZOP_{data.get('node_name','report').replace(' ','_')}.json",
                mime="application/json",use_container_width=True)

else:
    st.markdown("""<div class="empty-state">
        <div class="empty-state-icon">🛡️</div>
        <div class="empty-state-text">DESCRIBE YOUR PROCESS NODE ABOVE AND CLICK RUN HAZOP</div>
        <div class="empty-state-sub">Or select Industry → Equipment from sidebar and click Load</div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# STICKY FOOTER
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class="sticky-footer">
  <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#334155;letter-spacing:1.5px">
    IEC 61882 &nbsp;·&nbsp; GROQ LLAMA 3.3 70B &nbsp;·&nbsp; NOT A SUBSTITUTE FOR CERTIFIED HAZOP STUDY
  </div>
  <div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.9rem">
    <span style="color:#22c55e;font-weight:700">Developed by</span>
    <span style="color:#ffffff;font-weight:700"> Zunair Shahzad</span>
    <span style="color:#fbbf24;font-weight:600"> &nbsp;·&nbsp; UET Lahore</span>
    <span style="color:#ffffff;font-weight:400"> (New Campus)</span>
    <span style="color:#475569;font-size:0.78rem;margin-left:10px">· AI-Powered Engineering Series</span>
  </div>
</div>""", unsafe_allow_html=True)
