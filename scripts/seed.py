# Run with: python -m scripts.seed base
from app.db.postgres import SessionLocal
from app.repositories import role_repo, user_repo
from app.utils.hashing import hash_password
from app.config.settings import settings

BASE_ROLES = ["admin", "staff"]
BASE_PERMS = [
    "users.read", "users.write", "users.delete",
    "files.read", "files.write", "files.delete",
    "auth.read"
]
ROLE_PERMS = {
    "admin": BASE_PERMS,
    "staff": ["users.read", "files.read", "auth.read"]
}

def seed_base():
    db = SessionLocal()
    try:
        # 1) Roles & permissions
        role_map = {name: role_repo.upsert_role(db, name) for name in BASE_ROLES}
        perm_map = {code: role_repo.upsert_permission(db, code) for code in BASE_PERMS}
        for role_name, perms in ROLE_PERMS.items():
            r = role_map[role_name]
            for code in perms:
                role_repo.ensure_role_permission(db, r, perm_map[code])

        # 2) Admin user (from env or defaults)
        admin_email = getattr(settings, "ADMIN_EMAIL", None) or "admin@example.com"
        admin_pass = getattr(settings, "ADMIN_PASSWORD", None) or "secret"
        admin_name = "Administrator"

        u = user_repo.get_by_email(db, admin_email)
        if not u:
            u = user_repo.create(
                db,
                email=admin_email,
                name=admin_name,
                password_hash=hash_password(admin_pass),
            )
        role_repo.ensure_user_role(db, u.id, role_map["admin"])
        print(f"Seeded base roles/permissions and admin user: {admin_email}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "base"
    if cmd == "base":
        seed_base()
    else:
        print("Unknown seed. Try: python -m scripts.seed base")
