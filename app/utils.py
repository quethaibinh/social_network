from passlib.context import CryptContext #dung cho password


# dung cho thuat toan bam password (hash password)
pwt_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

def hashed(password: str):
    return pwt_context.hash(password)

# ham nay se tu dong so sanh mat khau duoc nhap(plain_password) va mat khau da duoc ma hoa bam trong csdl(hash_password)
# tra ve true - false
def verify(plain_password, hashed_password):
    return pwt_context.verify(plain_password, hashed_password)