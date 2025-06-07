import uuid
import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from domain.organization.repositories.refresh_token_repository import RefreshTokenRepository
from infrastructure.db.models.refresh_token_model import RefreshTokenModel


class RefreshTokenRepositoryImpl(RefreshTokenRepository):
    """Database implementation of refresh token repository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save_refresh_token(
        self,
        user_id: uuid.UUID,
        token: str,
        jti: str,
        expires_at: datetime,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Save refresh token and return token ID."""
        # Hash the token for security (don't store raw tokens)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        model = RefreshTokenModel(
            user_id=user_id,
            token_hash=token_hash,
            jti=jti,
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self._session.add(model)
        await self._session.flush()
        
        return str(model.id)
    
    async def get_refresh_token_by_jti(self, jti: str) -> Optional[RefreshTokenModel]:
        """Get refresh token by JWT ID."""
        result = await self._session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.jti == jti)
            .where(RefreshTokenModel.is_revoked == False)
        )
        return result.scalar_one_or_none()
    
    async def revoke_refresh_token_by_jti(self, jti: str) -> bool:
        """Revoke specific refresh token by JWT ID."""
        result = await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.jti == jti)
            .values(
                is_revoked=True,
                revoked_at=datetime.now(timezone.utc)
            )
        )
        return result.rowcount > 0
      
    async def revoke_refresh_token_by_id(self, token_id: str) -> bool:
        """Revoke specific refresh token by database ID."""
        try:
            # Convert string UUID to UUID object
            token_uuid = uuid.UUID(token_id)
            print(f"DEBUG: Attempting to revoke token with ID: {token_id} (UUID: {token_uuid})")
            
            # First, check if the token exists
            check_result = await self._session.execute(
                select(RefreshTokenModel)
                .where(RefreshTokenModel.id == token_uuid)
            )
            existing_token = check_result.scalar_one_or_none()
            
            if not existing_token:
                print(f"DEBUG: Token with ID {token_id} not found in database")
                return False
            
            print(f"DEBUG: Found token. Current revoked status: {existing_token.is_revoked}")
            
            if existing_token.is_revoked:
                print(f"DEBUG: Token {token_id} is already revoked")
                return False
            
            # Now revoke the token
            result = await self._session.execute(
                update(RefreshTokenModel)
                .where(RefreshTokenModel.id == token_uuid)
                .values(
                    is_revoked=True,
                    revoked_at=datetime.now(timezone.utc)
                )
            )
            
            success = result.rowcount > 0
            print(f"DEBUG: Revocation result - rows affected: {result.rowcount}, success: {success}")
            return success
        except Exception as e:
            print(f"Error revoking token by ID {token_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def revoke_all_user_refresh_tokens(self, user_id: uuid.UUID) -> int:
        """Revoke all refresh tokens for a user."""
        result = await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.is_revoked == False)
            .values(
                is_revoked=True,
                revoked_at=datetime.now(timezone.utc)
            )
        )
        return result.rowcount
    
    async def get_user_active_sessions(
        self, 
        user_id: uuid.UUID, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get all active refresh tokens/sessions for a user with pagination."""
        offset = (page - 1) * page_size
        
        # Get total count
        count_result = await self._session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.is_revoked == False)
            .where(RefreshTokenModel.expires_at > datetime.now(timezone.utc))
        )
        total_count = len(count_result.scalars().all())
        
        # Get paginated results
        result = await self._session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.is_revoked == False)
            .where(RefreshTokenModel.expires_at > datetime.now(timezone.utc))
            .order_by(RefreshTokenModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        
        sessions: List[Dict[str, Any]] = []
        for model in result.scalars().all():
            sessions.append({
                "id": str(model.id),
                "device_info": model.device_info,
                "ip_address": model.ip_address,
                "user_agent": model.user_agent,
                "created_at": model.created_at,
                "expires_at": model.expires_at
            })
        
        return {
            "sessions": sessions,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }
    
    async def get_user_revoked_sessions(
        self, 
        user_id: uuid.UUID, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get all revoked refresh tokens/sessions for a user with pagination."""
        offset = (page - 1) * page_size
        
        # Get total count
        count_result = await self._session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.is_revoked == True)
        )
        total_count = len(count_result.scalars().all())
        
        # Get paginated results
        result = await self._session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.is_revoked == True)
            .order_by(RefreshTokenModel.revoked_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        
        sessions: List[Dict[str, Any]] = []
        for model in result.scalars().all():
            sessions.append({
                "id": str(model.id),
                "device_info": model.device_info,
                "ip_address": model.ip_address,
                "user_agent": model.user_agent,
                "created_at": model.created_at,
                "expires_at": model.expires_at,
                "revoked_at": model.revoked_at
            })
        
        return {
            "sessions": sessions,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }
    
    async def cleanup_expired_tokens(self) -> int:
        """Remove expired refresh tokens."""
        result = await self._session.execute(
            delete(RefreshTokenModel)
            .where(RefreshTokenModel.expires_at < datetime.now(timezone.utc))
        )
        return result.rowcount
    
    def _group_sessions_by_device(self, sessions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Helper method to group sessions by device info."""
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for session in sessions:
            device_key = session.get("device_info", "Unknown Device")
            if device_key not in grouped:
                grouped[device_key] = []
            grouped[device_key].append(session)
        return grouped
    
    def _group_sessions_by_ip(self, sessions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Helper method to group sessions by IP address."""
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for session in sessions:
            ip_key = session.get("ip_address", "Unknown IP")
            if ip_key not in grouped:
                grouped[ip_key] = []
            grouped[ip_key].append(session)
        return grouped
    
    async def get_user_active_sessions_grouped_by_device(
        self, 
        user_id: uuid.UUID, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get active sessions grouped by device."""
        # First get all active sessions for the user (without pagination to group properly)
        result = await self._session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.is_revoked == False)
            .where(RefreshTokenModel.expires_at > datetime.now(timezone.utc))
            .order_by(RefreshTokenModel.created_at.desc())
        )
        
        all_sessions: List[Dict[str, Any]] = []
        for model in result.scalars().all():
            all_sessions.append({
                "id": str(model.id),
                "device_info": model.device_info,
                "ip_address": model.ip_address,
                "user_agent": model.user_agent,
                "created_at": model.created_at,
                "expires_at": model.expires_at
            })
        
        # Group by device
        grouped_sessions = self._group_sessions_by_device(all_sessions)
        
        # Apply pagination to groups
        devices = list(grouped_sessions.keys())
        total_devices = len(devices)
        offset = (page - 1) * page_size
        paginated_devices = devices[offset:offset + page_size]
        
        paginated_grouped = {device: grouped_sessions[device] for device in paginated_devices}
        
        return {
            "grouped_sessions": paginated_grouped,
            "total_sessions": len(all_sessions),
            "total_devices": total_devices,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_devices + page_size - 1) // page_size
        }
    
    async def get_user_active_sessions_grouped_by_ip(
        self, 
        user_id: uuid.UUID, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get active sessions grouped by IP address."""
        # First get all active sessions for the user (without pagination to group properly)
        result = await self._session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.is_revoked == False)
            .where(RefreshTokenModel.expires_at > datetime.now(timezone.utc))
            .order_by(RefreshTokenModel.created_at.desc())
        )
        
        all_sessions: List[Dict[str, Any]] = []
        for model in result.scalars().all():
            all_sessions.append({
                "id": str(model.id),
                "device_info": model.device_info,
                "ip_address": model.ip_address,
                "user_agent": model.user_agent,
                "created_at": model.created_at,
                "expires_at": model.expires_at
            })
        
        # Group by IP
        grouped_sessions = self._group_sessions_by_ip(all_sessions)
        
        # Apply pagination to groups
        ips = list(grouped_sessions.keys())
        total_ips = len(ips)
        offset = (page - 1) * page_size
        paginated_ips = ips[offset:offset + page_size]
        
        paginated_grouped = {ip: grouped_sessions[ip] for ip in paginated_ips}
        
        return {
            "grouped_sessions": paginated_grouped,
            "total_sessions": len(all_sessions),
            "total_ips": total_ips,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_ips + page_size - 1) // page_size
        }
    
    async def get_user_revoked_sessions_grouped_by_device(
        self, 
        user_id: uuid.UUID, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get revoked sessions grouped by device."""
        # First get all revoked sessions for the user (without pagination to group properly)
        result = await self._session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.is_revoked == True)
            .order_by(RefreshTokenModel.revoked_at.desc())
        )
        
        all_sessions: List[Dict[str, Any]] = []
        for model in result.scalars().all():
            all_sessions.append({
                "id": str(model.id),
                "device_info": model.device_info,
                "ip_address": model.ip_address,
                "user_agent": model.user_agent,
                "created_at": model.created_at,
                "expires_at": model.expires_at,
                "revoked_at": model.revoked_at
            })
        
        # Group by device
        grouped_sessions = self._group_sessions_by_device(all_sessions)
        
        # Apply pagination to groups
        devices = list(grouped_sessions.keys())
        total_devices = len(devices)
        offset = (page - 1) * page_size
        paginated_devices = devices[offset:offset + page_size]
        
        paginated_grouped = {device: grouped_sessions[device] for device in paginated_devices}
        
        return {
            "grouped_sessions": paginated_grouped,
            "total_sessions": len(all_sessions),
            "total_devices": total_devices,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_devices + page_size - 1) // page_size
        }
    
    async def get_user_revoked_sessions_grouped_by_ip(
        self, 
        user_id: uuid.UUID, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get revoked sessions grouped by IP address."""
        # First get all revoked sessions for the user (without pagination to group properly)
        result = await self._session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.is_revoked == True)
            .order_by(RefreshTokenModel.revoked_at.desc())
        )
        
        all_sessions: List[Dict[str, Any]] = []
        for model in result.scalars().all():
            all_sessions.append({
                "id": str(model.id),
                "device_info": model.device_info,
                "ip_address": model.ip_address,
                "user_agent": model.user_agent,
                "created_at": model.created_at,
                "expires_at": model.expires_at,
                "revoked_at": model.revoked_at
            })
        
        # Group by IP
        grouped_sessions = self._group_sessions_by_ip(all_sessions)
        
        # Apply pagination to groups
        ips = list(grouped_sessions.keys())
        total_ips = len(ips)
        offset = (page - 1) * page_size
        paginated_ips = ips[offset:offset + page_size]
        
        paginated_grouped = {ip: grouped_sessions[ip] for ip in paginated_ips}
        
        return {
            "grouped_sessions": paginated_grouped,
            "total_sessions": len(all_sessions),
            "total_ips": total_ips,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_ips + page_size - 1) // page_size
        }