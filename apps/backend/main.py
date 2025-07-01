from fastapi import FastAPI
from leads import encontrar_leads_dic_fic

app = FastAPI()

@app.get("/leads")
def get_leads():
    leads = encontrar_leads_dic_fic()
    return {"total": len(leads), "leads": leads}
