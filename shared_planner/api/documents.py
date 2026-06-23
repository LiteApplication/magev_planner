import os
import shutil
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import select

from shared_planner.api.auth import CurrentAdmin
from shared_planner.db.models import Document
from shared_planner.db.session import SessionLock
from shared_planner.db.settings import get

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = "uploads"
MAX_SIZE = 25 * 1024 * 1024  # 25 MB


def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def _public_url(stored_name: str) -> str:
    base = get("base_domain").value.rstrip("/")
    return f"{base}/api/documents/{stored_name}/raw"


class DocumentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    size: int
    url: str

    @classmethod
    def from_document(cls, doc: Document) -> "DocumentOut":
        return cls(
            id=doc.id,
            filename=doc.filename,
            content_type=doc.content_type,
            size=doc.size,
            url=_public_url(doc.stored_name),
        )


@router.get("/list", dependencies=[Depends(CurrentAdmin)])
def list_documents() -> list[DocumentOut]:
    with SessionLock() as session:
        docs = session.exec(select(Document).order_by(Document.created_at.desc())).all()
        result = [DocumentOut.from_document(d) for d in docs]
    return result


@router.post("/upload", dependencies=[Depends(CurrentAdmin)])
def upload_document(file: UploadFile) -> DocumentOut:
    ensure_upload_dir()
    ext = os.path.splitext(file.filename or "")[1][:16]
    stored_name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, stored_name)

    with open(path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    size = os.path.getsize(path)
    if size > MAX_SIZE:
        os.remove(path)
        raise HTTPException(status_code=413, detail="error.document.too_large")

    with SessionLock() as session:
        doc = Document(
            filename=os.path.basename(file.filename or stored_name),
            stored_name=stored_name,
            content_type=file.content_type or "application/octet-stream",
            size=size,
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        result = DocumentOut.from_document(doc)
    return result


@router.get("/{stored_name}/raw")
def get_document_raw(stored_name: str):
    """Public endpoint so the file can be embedded by URL in emails.

    Addressed by the unguessable stored name (a uuid + extension) rather than
    the sequential id, so documents are not enumerable.
    """
    with SessionLock() as session:
        doc = session.exec(
            select(Document).where(Document.stored_name == stored_name)
        ).first()
        if doc is None:
            raise HTTPException(status_code=404, detail="error.document.not_found")
        path = os.path.join(UPLOAD_DIR, doc.stored_name)
        filename = doc.filename
        content_type = doc.content_type
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="error.document.not_found")
    return FileResponse(
        path,
        media_type=content_type,
        filename=filename,
        content_disposition_type="inline",
    )


@router.delete("/{document_id}/delete", dependencies=[Depends(CurrentAdmin)])
def delete_document(document_id: int) -> None:
    with SessionLock() as session:
        doc = session.get(Document, document_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="error.document.not_found")
        path = os.path.join(UPLOAD_DIR, doc.stored_name)
        if os.path.isfile(path):
            os.remove(path)
        session.delete(doc)
        session.commit()
