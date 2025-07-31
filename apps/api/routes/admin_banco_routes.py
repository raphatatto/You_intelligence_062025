
# @router.post("/dashboard/refresh")
# async def atualizar_materializadas(db: AsyncSession = Depends(get_session)):
#     await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.mv_lead_completo_detalhado"))
#     await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.resumo_leads_distribuidora"))
#     await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.resumo_energia_municipio"))
#     await db.execute(text("REFRESH MATERIALIZED VIEW intel_lead.resumo_leads_ano_camada"))
#     await db.commit()
#     return {"status": "ok", "msg": "Materializadas atualizadas com sucesso"}
