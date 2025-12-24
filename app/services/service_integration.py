"""Service Integration

HTTP client for integrating with other microservices.
"""

import httpx
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.config import settings
from app.schemas.search import IndexDocumentRequest
from app.models.search_index import DocumentType


class ServiceIntegration:
    """Client for integrating with other microservices."""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
    
    async def fetch_content_articles(self) -> List[IndexDocumentRequest]:
        """Fetch articles from Content Service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{settings.CONTENT_SERVICE_URL}/api/v1/articles",
                    params={"page": 1, "page_size": 1000}
                )
                response.raise_for_status()
                data = response.json()
                
                documents = []
                for article in data.get("items", []):
                    documents.append(IndexDocumentRequest(
                        document_id=UUID(article["id"]),
                        document_type=DocumentType.ARTICLE,
                        title=article.get("title", ""),
                        content=article.get("content", ""),
                        language=article.get("language", "en"),
                        metadata={
                            "tags": article.get("tags", []),
                            "category": article.get("category")
                        },
                        author_id=UUID(article["author_id"]) if article.get("author_id") else None,
                        author_name=article.get("author_name"),
                        status=article.get("status"),
                        published_at=article.get("published_at")
                    ))
                
                return documents
        except Exception as e:
            print(f"Error fetching articles from Content Service: {str(e)}")
            return []
    
    async def fetch_partners(self) -> List[IndexDocumentRequest]:
        """Fetch partners from Partners CRM Service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{settings.PARTNERS_CRM_SERVICE_URL}/api/v1/partners",
                    params={"page": 1, "page_size": 1000}
                )
                response.raise_for_status()
                data = response.json()
                
                documents = []
                for partner in data.get("items", []):
                    # Combine fields for searchable content
                    content = f"{partner.get('description', '')} {partner.get('mission', '')} {partner.get('location', '')}"
                    
                    documents.append(IndexDocumentRequest(
                        document_id=UUID(partner["id"]),
                        document_type=DocumentType.PARTNER,
                        title=partner.get("name", ""),
                        content=content,
                        language=partner.get("language", "en"),
                        metadata={
                            "type": partner.get("type"),
                            "location": partner.get("location"),
                            "status": partner.get("status")
                        },
                        status=partner.get("status")
                    ))
                
                return documents
        except Exception as e:
            print(f"Error fetching partners from Partners CRM Service: {str(e)}")
            return []
    
    async def fetch_projects(self) -> List[IndexDocumentRequest]:
        """Fetch projects from Projects Service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{settings.PROJECTS_SERVICE_URL}/api/v1/projects",
                    params={"page": 1, "page_size": 1000}
                )
                response.raise_for_status()
                data = response.json()
                
                documents = []
                for project in data.get("items", []):
                    documents.append(IndexDocumentRequest(
                        document_id=UUID(project["id"]),
                        document_type=DocumentType.PROJECT,
                        title=project.get("name", ""),
                        content=project.get("description", ""),
                        language=project.get("language", "en"),
                        metadata={
                            "category": project.get("category"),
                            "location": project.get("location"),
                            "budget": project.get("budget")
                        },
                        status=project.get("status")
                    ))
                
                return documents
        except Exception as e:
            print(f"Error fetching projects from Projects Service: {str(e)}")
            return []
    
    async def fetch_social_posts(self) -> List[IndexDocumentRequest]:
        """Fetch social media posts from Social Media Service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{settings.SOCIAL_MEDIA_SERVICE_URL}/api/v1/posts",
                    params={"page": 1, "page_size": 1000}
                )
                response.raise_for_status()
                data = response.json()
                
                documents = []
                for post in data.get("items", []):
                    documents.append(IndexDocumentRequest(
                        document_id=UUID(post["id"]),
                        document_type=DocumentType.SOCIAL_POST,
                        title=post.get("content", "")[:100],  # First 100 chars as title
                        content=post.get("content", ""),
                        language=post.get("language", "en"),
                        metadata={
                            "platform": post.get("platform"),
                            "media_type": post.get("media_type")
                        },
                        author_id=UUID(post["author_id"]) if post.get("author_id") else None,
                        author_name=post.get("author_name"),
                        status=post.get("status"),
                        published_at=post.get("published_at")
                    ))
                
                return documents
        except Exception as e:
            print(f"Error fetching posts from Social Media Service: {str(e)}")
            return []
    
    async def fetch_notifications(self) -> List[IndexDocumentRequest]:
        """Fetch notifications from Notification Service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications",
                    params={"page": 1, "page_size": 1000}
                )
                response.raise_for_status()
                data = response.json()
                
                documents = []
                for notification in data.get("items", []):
                    documents.append(IndexDocumentRequest(
                        document_id=UUID(notification["id"]),
                        document_type=DocumentType.NOTIFICATION,
                        title=notification.get("title", ""),
                        content=notification.get("message", ""),
                        language=notification.get("language", "en"),
                        metadata={
                            "type": notification.get("type"),
                            "priority": notification.get("priority")
                        },
                        status=notification.get("status")
                    ))
                
                return documents
        except Exception as e:
            print(f"Error fetching notifications from Notification Service: {str(e)}")
            return []
    
    async def fetch_all_documents(self) -> List[IndexDocumentRequest]:
        """Fetch all documents from all services."""
        all_documents = []
        
        # Fetch from all services in parallel would be better, but for simplicity:
        all_documents.extend(await self.fetch_content_articles())
        all_documents.extend(await self.fetch_partners())
        all_documents.extend(await self.fetch_projects())
        all_documents.extend(await self.fetch_social_posts())
        all_documents.extend(await self.fetch_notifications())
        
        return all_documents
