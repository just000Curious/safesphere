import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        result = await session.execute(select(User).where(User.email == "admin@safesphere.com"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                email="admin@safesphere.com",
                name="System Admin",
                phone="1234567890",
                password_hash=get_password_hash("adminpassword"),
                role="admin",
                is_verified=True
            )
            session.add(admin)
            print("Admin user created: admin@safesphere.com / adminpassword")
        else:
            print("Admin user already exists.")

        # Check if regular user already exists
        result = await session.execute(select(User).where(User.email == "user@safesphere.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                email="user@safesphere.com",
                name="Test User",
                phone="0987654321",
                password_hash=get_password_hash("userpassword"),
                role="user",
                is_verified=True
            )
            session.add(user)
            print("Test user created: user@safesphere.com / userpassword")
        else:
            print("Test user already exists.")

        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_data())
