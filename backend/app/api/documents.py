"""
Documents API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentDetail, APIResponse
)
from app.database import db
from app.dependencies import get_current_user
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=APIResponse)
async def get_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tag: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = Query("updated_at", regex="^(created_at|updated_at)$"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of documents
    """
    with db.get_connection() as conn:
        # Build query
        base_query = "FROM documents d WHERE user_id = ?"
        params = [current_user["user_id"]]

        if tag:
            base_query += """
                AND EXISTS (
                    SELECT 1 FROM document_tags
                    WHERE document_id = d.document_id AND tag_name = ?
                )
            """
            params.append(tag)

        if keyword:
            base_query += " AND (title LIKE ? OR content LIKE ? OR summary LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        # Get total count
        count_query = f"SELECT COUNT(*) as total {base_query}"
        cursor = conn.execute(count_query, params)
        total = cursor.fetchone()["total"]

        # Get documents with tags
        offset = (page - 1) * page_size
        order = "DESC" if sort_by == "updated_at" else "DESC"
        query = f"""
            SELECT
                d.document_id, d.title, d.summary, d.created_at, d.updated_at,
                GROUP_CONCAT(dt.tag_name) as tags
            FROM documents d
            LEFT JOIN document_tags dt ON d.document_id = dt.document_id
            WHERE d.user_id = ?
            GROUP BY d.document_id
            ORDER BY d.{sort_by} {order}
            LIMIT ? OFFSET ?
        """

        # Re-apply filters in main query
        filter_params = []
        if tag:
            query = f"""
                SELECT
                    d.document_id, d.title, d.summary, d.created_at, d.updated_at,
                    GROUP_CONCAT(dt.tag_name) as tags
                FROM documents d
                LEFT JOIN document_tags dt ON d.document_id = dt.document_id
                WHERE d.user_id = ?
                    AND EXISTS (
                        SELECT 1 FROM document_tags dt2
                        WHERE dt2.document_id = d.document_id AND dt2.tag_name = ?
                    )
                GROUP BY d.document_id
                ORDER BY d.{sort_by} {order}
                LIMIT ? OFFSET ?
            """
            cursor = conn.execute(query, [current_user["user_id"], tag, page_size, offset])
        elif keyword:
            query = f"""
                SELECT
                    d.document_id, d.title, d.summary, d.created_at, d.updated_at,
                    GROUP_CONCAT(dt.tag_name) as tags
                FROM documents d
                LEFT JOIN document_tags dt ON d.document_id = dt.document_id
                WHERE d.user_id = ? AND (d.title LIKE ? OR d.content LIKE ? OR d.summary LIKE ?)
                GROUP BY d.document_id
                ORDER BY d.{sort_by} {order}
                LIMIT ? OFFSET ?
            """
            cursor = conn.execute(query, [
                current_user["user_id"],
                f"%{keyword}%", f"%{keyword}%", f"%{keyword}%",
                page_size, offset
            ])
        else:
            cursor = conn.execute(query, [current_user["user_id"], page_size, offset])

        documents = []
        for row in cursor.fetchall():
            documents.append({
                "document_id": row["document_id"],
                "title": row["title"],
                "summary": row["summary"],
                "tags": row["tags"].split(",") if row["tags"] else [],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })

    return APIResponse(
        code=200,
        message="success",
        data={
            "total": total,
            "items": documents
        }
    )


@router.get("/{document_id}", response_model=APIResponse)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get document details
    """
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM documents
            WHERE document_id = ? AND user_id = ?
        """, (document_id, current_user["user_id"]))

        document = cursor.fetchone()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Get tags
        cursor = conn.execute("""
            SELECT tag_name FROM document_tags
            WHERE document_id = ?
        """, (document_id,))

        tags = [row["tag_name"] for row in cursor.fetchall()]

    return APIResponse(
        code=200,
        message="success",
        data={
            "document_id": document["document_id"],
            "title": document["title"],
            "content": document["content"],
            "summary": document["summary"],
            "tags": tags,
            "source_conversation_id": document["source_conversation_id"],
            "created_at": document["created_at"],
            "updated_at": document["updated_at"]
        }
    )


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    doc_data: DocumentCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new document
    """
    document_id = db.generate_uuid()
    now = datetime.utcnow()

    with db.get_connection() as conn:
        conn.execute("""
            INSERT INTO documents
            (document_id, user_id, title, content, summary, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (document_id, current_user["user_id"], doc_data.title,
              doc_data.content, doc_data.summary, now, now))

        # Add tags
        for tag in doc_data.tags:
            tag_id = db.generate_uuid()
            conn.execute("""
                INSERT INTO document_tags (tag_id, document_id, tag_name)
                VALUES (?, ?, ?)
            """, (tag_id, document_id, tag))

    return APIResponse(
        code=201,
        message="创建成功",
        data={
            "document_id": document_id,
            "title": doc_data.title,
            "created_at": now
        }
    )


@router.put("/{document_id}", response_model=APIResponse)
async def update_document(
    document_id: str,
    doc_data: DocumentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a document
    """
    with db.get_connection() as conn:
        # Check ownership
        cursor = conn.execute("""
            SELECT user_id FROM documents
            WHERE document_id = ?
        """, (document_id,))

        document = cursor.fetchone()
        if not document or document["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Build update query
        updates = []
        params = []
        if doc_data.title:
            updates.append("title = ?")
            params.append(doc_data.title)
        if doc_data.content:
            updates.append("content = ?")
            params.append(doc_data.content)
        if doc_data.summary is not None:
            updates.append("summary = ?")
            params.append(doc_data.summary)

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.utcnow())
            params.append(document_id)

            query = f"UPDATE documents SET {', '.join(updates)} WHERE document_id = ?"
            conn.execute(query, params)

        # Update tags if provided
        if doc_data.tags is not None:
            # Delete existing tags
            conn.execute("""
                DELETE FROM document_tags
                WHERE document_id = ?
            """, (document_id,))

            # Add new tags
            for tag in doc_data.tags:
                tag_id = db.generate_uuid()
                conn.execute("""
                    INSERT INTO document_tags (tag_id, document_id, tag_name)
                    VALUES (?, ?, ?)
                """, (tag_id, document_id, tag))

    return APIResponse(
        code=200,
        message="更新成功",
        data={
            "document_id": document_id,
            "title": doc_data.title or "",
            "updated_at": datetime.utcnow()
        }
    )


@router.delete("/{document_id}", response_model=APIResponse)
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a document
    """
    with db.get_connection() as conn:
        # Check ownership
        cursor = conn.execute("""
            SELECT user_id FROM documents
            WHERE document_id = ?
        """, (document_id,))

        document = cursor.fetchone()
        if not document or document["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Delete tags first
        conn.execute("""
            DELETE FROM document_tags
            WHERE document_id = ?
        """, (document_id,))

        # Delete document
        conn.execute("""
            DELETE FROM documents
            WHERE document_id = ?
        """, (document_id,))

    return APIResponse(
        code=200,
        message="删除成功"
    )


@router.get("/search", response_model=APIResponse)
async def search_documents(
    q: str = Query(..., min_length=1),
    tags: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Search documents by keyword and tags
    """
    with db.get_connection() as conn:
        # Build query
        base_query = "FROM documents d WHERE user_id = ? AND (title LIKE ? OR content LIKE ? OR summary LIKE ?)"
        params = [current_user["user_id"], f"%{q}%", f"%{q}%", f"%{q}%"]

        if tags:
            tag_list = tags.split(",")
            for tag in tag_list:
                base_query += """
                    AND EXISTS (
                        SELECT 1 FROM document_tags
                        WHERE document_id = d.document_id AND tag_name = ?
                    )
                """
                params.append(tag.strip())

        # Get total count
        count_query = f"SELECT COUNT(*) as total {base_query}"
        cursor = conn.execute(count_query, params)
        total = cursor.fetchone()["total"]

        # Get documents
        offset = (page - 1) * page_size
        query = f"""
            SELECT
                d.document_id, d.title, d.summary, d.created_at, d.updated_at,
                GROUP_CONCAT(dt.tag_name) as tags
            FROM documents d
            LEFT JOIN document_tags dt ON d.document_id = dt.document_id
            WHERE d.user_id = ? AND (d.title LIKE ? OR d.content LIKE ? OR d.summary LIKE ?)
            GROUP BY d.document_id
            ORDER BY d.updated_at DESC
            LIMIT ? OFFSET ?
        """

        cursor = conn.execute(query, [
            current_user["user_id"],
            f"%{q}%", f"%{q}%", f"%{q}%",
            page_size, offset
        ])

        documents = []
        for row in cursor.fetchall():
            documents.append({
                "document_id": row["document_id"],
                "title": row["title"],
                "summary": row["summary"],
                "tags": row["tags"].split(",") if row["tags"] else [],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })

    return APIResponse(
        code=200,
        message="success",
        data={
            "total": total,
            "items": documents
        }
    )
