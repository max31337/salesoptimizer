#!/usr/bin/env python3
"""
Superadmin Constraint Manager - Tool to validate and enforce single superadmin constraint.
This script helps manage the system's superadmin constraints and provides utilities to check and fix violations.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.db.database import get_database_url
from domain.organization.services.superadmin_management_service import SuperadminManagementService


def check_superadmin_constraints():
    """Check current superadmin constraints and display status."""
    print("🔍 Checking Superadmin Constraints...")
    print("=" * 60)
    
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        service = SuperadminManagementService(session)
        validation = service.validate_single_superadmin_constraint()
        
        print(f"📊 Current Status:")
        print(f"   Total superadmins: {validation['current_count']}")
        print(f"   Maximum allowed: {validation['max_allowed']}")
        print(f"   Constraint valid: {'✅ Yes' if validation['is_valid'] else '❌ No'}")
        
        if validation['violation_message']:
            print(f"   Issue: {validation['violation_message']}")
        
        print(f"\n👥 Superadmins in system:")
        if validation['superadmins']:
            for i, admin in enumerate(validation['superadmins'], 1):
                print(f"   {i}. {admin['email']}")
                print(f"      ID: {admin['id']}")
                print(f"      Username: {admin['username']}")
                print(f"      Created: {admin['created_at'] or 'Unknown'}")
                print()
        else:
            print("   No superadmins found in the system.")
        
        return validation


def enforce_superadmin_constraints(keep_latest: bool = True, auto_confirm: bool = False):
    """Enforce single superadmin constraint."""
    print("🛠️  Enforcing Superadmin Constraints...")
    print("=" * 60)
    
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        service = SuperadminManagementService(session)
        validation = service.validate_single_superadmin_constraint()
        
        if validation['is_valid']:
            print("✅ System constraints are already satisfied!")
            print(f"   Current superadmins: {validation['current_count']}")
            return validation
        
        print(f"⚠️  Constraint violation detected:")
        print(f"   Found {validation['current_count']} superadmins, maximum allowed is {validation['max_allowed']}")
        
        print(f"\n👥 Current superadmins:")
        for i, admin in enumerate(validation['superadmins'], 1):
            print(f"   {i}. {admin['email']} (Created: {admin['created_at'] or 'Unknown'})")
        
        strategy = "most recent" if keep_latest else "oldest"
        print(f"\n🎯 Strategy: Keep the {strategy} superadmin, demote others to org_admin")
        
        if not auto_confirm:
            response = input(f"\nProceed with enforcement? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("❌ Operation cancelled by user.")
                return validation
        
        # Enforce constraint
        result = service.ensure_single_superadmin_constraint(keep_latest=keep_latest)
        session.commit()
        
        print(f"\n✅ {result['message']}")
        
        if result['action'] == 'constraint_enforced':
            print(f"\n🎉 Constraint enforcement completed:")
            print(f"   Kept superadmin: {result['kept_superadmin']['email']}")
            print(f"   Strategy used: {result['strategy']}")
            
            if result['demoted_superadmins']:
                print(f"\n📝 Demoted to org_admin ({len(result['demoted_superadmins'])} users):")
                for demoted in result['demoted_superadmins']:
                    print(f"   - {demoted['email']} (ID: {demoted['id']})")
        
        return result


def main():
    """Main function to run superadmin constraint management."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Superadmin Constraint Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/superadmin_constraint_manager.py --check
  python scripts/superadmin_constraint_manager.py --enforce
  python scripts/superadmin_constraint_manager.py --enforce --keep-oldest
  python scripts/superadmin_constraint_manager.py --enforce --auto-confirm
        """
    )
    
    parser.add_argument(
        "--check", 
        action="store_true", 
        help="Check current superadmin constraints (default action)"
    )
    
    parser.add_argument(
        "--enforce", 
        action="store_true", 
        help="Enforce single superadmin constraint"
    )
    
    parser.add_argument(
        "--keep-oldest", 
        action="store_true", 
        help="When enforcing, keep the oldest superadmin instead of the newest"
    )
    
    parser.add_argument(
        "--auto-confirm", 
        action="store_true", 
        help="Skip confirmation prompts (use with caution)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.enforce:
            keep_latest = not args.keep_oldest
            enforce_superadmin_constraints(
                keep_latest=keep_latest,
                auto_confirm=args.auto_confirm
            )
        else:
            # Default action is to check
            check_superadmin_constraints()
        
        print("\n✨ Operation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
