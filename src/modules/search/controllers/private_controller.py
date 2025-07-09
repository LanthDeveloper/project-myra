from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException
from fastapi.responses import Response
from modules.search.utils.validacion_personas import validacion_total
import tempfile

async def process_excel(request: Request, response: Response):
    try:
        form = await request.form()
        file = form.get("file")

        if file is None:
            raise HTTPException(status_code=400, detail="No se envió ningún archivo")

        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="El archivo debe ser un Excel (.xlsx o .xls)")

        contents = await file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        resultado, _ = await validacion_total(excel_path=tmp_path)

        return JSONResponse(content={
            "success": True,
            "data": resultado["data"],
            "urlExcel": resultado["url"]
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo procesar el archivo: {str(e)}")
