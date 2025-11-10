from auth import Auth

print("🔍 Debug: Obteniendo todos los usuarios...")
users = Auth.get_all_users()

print(f"📊 Total usuarios encontrados: {len(users)}")
for user in users:
    print(f"ID: {user['id']}, Email: {user['email']}, Nombre: {user['nombre']}")