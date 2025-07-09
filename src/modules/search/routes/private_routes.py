# src/modules/search/routes/private_routes.py
from fastapi import APIRouter
from fastapi import Response
from modules.search.controllers.private_controller import process_excel
from fastapi import Request, Response

router = APIRouter()

@router.post("/process-excel")
async def process_excel_route(request: Request, response: Response):
    return await process_excel(request, response)



