import bcrypt

print bcrypt.hashpw("", bcrypt.gensalt())
