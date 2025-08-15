from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.role import Role, Permission, RolePermission, UserRole

# ----- Roles -----
def upsert_role(db: Session, name: str) -> Role:
    r = db.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
    if r: return r
    r = Role(name=name); db.add(r); db.commit(); db.refresh(r); return r

def get_role_by_name(db: Session, name: str) -> Role | None:
    return db.execute(select(Role).where(Role.name == name)).scalar_one_or_none()

# ----- Permissions -----
def upsert_permission(db: Session, code: str) -> Permission:
    p = db.execute(select(Permission).where(Permission.code == code)).scalar_one_or_none()
    if p: return p
    p = Permission(code=code); db.add(p); db.commit(); db.refresh(p); return p

# ----- Role ↔ Permission -----
def ensure_role_permission(db: Session, role: Role, perm: Permission) -> None:
    exists = db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == perm.id
        )
    ).scalar_one_or_none()
    if exists: return
    db.add(RolePermission(role_id=role.id, permission_id=perm.id))
    db.commit()

# ----- User ↔ Role -----
def ensure_user_role(db: Session, user_id: int, role: Role) -> None:
    exists = db.execute(
        select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role.id)
    ).scalar_one_or_none()
    if exists: return
    db.add(UserRole(user_id=user_id, role_id=role.id))
    db.commit()

def user_has_role(db: Session, user_id: int, role_name: str) -> bool:
    stmt = (
        select(Role.id)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id, Role.name == role_name)
    )
    return db.execute(stmt).scalar_one_or_none() is not None

def user_has_permission(db: Session, user_id: int, perm_code: str) -> bool:
    # roles -> role_permissions -> permissions
    stmt = (
        select(Permission.id)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id, Permission.code == perm_code)
    )
    return db.execute(stmt).scalar_one_or_none() is not None