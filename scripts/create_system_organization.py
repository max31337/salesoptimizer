#!/usr/bin/env python3
"""
Script to create the SalesOptimizer Platform system organization.
This organization is used for superadmins and platform management.
"""
import uuid
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.db.database import get_database_url
from infrastructure.db.models.tenant_model import TenantModel


def create_system_organization():
    """Create the SalesOptimizer Platform system organization."""
    
    # Database setup
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    # System organization details
    system_org_name = "SalesOptimizer Platform"
    system_org_slug = "salesoptimizer-platform"
    
    with SessionLocal() as session:
        # Check if system organization already exists
        existing_org = session.query(TenantModel).filter(
            TenantModel.name == system_org_name
        ).first()
        
        if existing_org:
            print(f"✅ System organization '{system_org_name}' already exists!")
            print(f"🆔 ID: {existing_org.id}")
            print(f"🏷️  Slug: {existing_org.slug}")
            return existing_org.id
        
        # Create system organization
        system_org = TenantModel(
            id=uuid.uuid4(),
            name=system_org_name,
            slug=system_org_slug,
            subscription_tier="system",
            is_active=True,
            owner_id=None,  # No single owner for system org
            settings={
                "is_system_organization": True,
                "description": "SalesOptimizer Platform system organization for superadmins and platform management",
                "created_by": "system_initialization"
            },
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        session.add(system_org)
        session.commit()
        
        print(f"✅ System organization created successfully!")
        print(f"📛 Name: {system_org_name}")
        print(f"🏷️  Slug: {system_org_slug}")
        print(f"🆔 ID: {system_org.id}")
        print(f"📊 Subscription Tier: system")
        
        return system_org.id


def get_or_create_system_organization():
    """Get existing system organization or create it if it doesn't exist."""
    
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        # Try to find existing system organization
        system_org = session.query(TenantModel).filter(
            TenantModel.name == "SalesOptimizer Platform"
        ).first()
        
        if system_org:
            return system_org.id
        
        # If not found, create it
        return create_system_organization()


if __name__ == "__main__":
    print("🚀 Creating SalesOptimizer Platform system organization...")
    create_system_organization()
    print("✨ Done!")
