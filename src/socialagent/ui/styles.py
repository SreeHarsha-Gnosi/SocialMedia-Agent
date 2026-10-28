CSS = """
<style>
#MainMenu, footer {visibility: hidden;}
.stApp {
  background: radial-gradient(1100px 600px at 10% -10%, rgba(99,102,241,.28), transparent 60%),
              radial-gradient(900px 500px at 100% 0%, rgba(20,184,166,.16), transparent 55%),
              #0B0B14;
}
.block-container {padding-top: 2rem; max-width: 1200px;}
.hero {padding: 1.6rem 1.8rem; border-radius: 22px; margin-bottom: 1.2rem;
  background: linear-gradient(135deg, rgba(99,102,241,.22), rgba(20,184,166,.12));
  border: 1px solid rgba(255,255,255,.08); backdrop-filter: blur(8px);}
.hero h1 {margin: 0; font-size: 2.1rem; letter-spacing: -.5px;
  background: linear-gradient(90deg,#A5B4FC,#5EEAD4,#FDE68A); -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;}
.hero p {margin: .4rem 0 0; color: #B4B4CC; font-size: 1rem;}
.chips {margin-top: .9rem; display: flex; gap: .5rem; flex-wrap: wrap;}
.chip {padding: .25rem .7rem; border-radius: 999px; font-size: .78rem;
  background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.1); color: #D8D8EE;}
.chip.ok {border-color: rgba(52,211,153,.5); color: #6EE7B7;}
.card {padding: 1.1rem 1.3rem; border-radius: 18px; background: rgba(20,20,43,.75);
  border: 1px solid rgba(255,255,255,.07); margin-bottom: 1rem;}
.step {font-size: .75rem; letter-spacing: .12em; text-transform: uppercase; color: #5EEAD4; font-weight: 700;}
.summary {border-left: 3px solid #14B8A6; padding: .6rem 1rem; color: #CFCFE6;
  background: rgba(20,184,166,.08); border-radius: 0 12px 12px 0; margin-bottom: 1rem;}
div.stButton > button[kind="primary"], div.stDownloadButton > button[kind="primary"] {
  background: linear-gradient(90deg,#6366F1,#14B8A6); border: 0; font-weight: 600;
  border-radius: 12px; padding: .6rem 1.2rem;}
div.stButton > button:hover {transform: translateY(-1px); transition: .15s;}
[data-testid="stFileUploaderDropzone"] {border: 2px dashed rgba(94,234,212,.5); border-radius: 18px;
  background: rgba(20,184,166,.06);}
.stTabs [data-baseweb="tab"] {font-weight: 600;}
.phone {background:#0F1A14; border-radius: 18px; padding: 1rem 1.1rem; border:1px solid rgba(255,255,255,.08);
  white-space: pre-wrap; color:#E7F5EC; font-size:.95rem; line-height:1.5;}
</style>
"""
