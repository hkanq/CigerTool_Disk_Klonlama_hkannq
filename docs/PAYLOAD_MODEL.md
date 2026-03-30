# Payload Modeli

Payload kaynakları `workspace/payload/` altında tutulur.

Geçerli merge hedefleri:

- `workspace/payload/Desktop` -> `Users\Public\Desktop`
- `workspace/payload/ProgramFiles` -> `Program Files`
- `workspace/payload/Users` -> `Users`
- `workspace/payload/Tools` -> USB `tools/`

Bu model sayesinde proje sahibi rebuild öncesinde:

- masaüstüne dosya bırakabilir
- ek program klasörleri ekleyebilir
- kullanıcı profili içeriği hazırlayabilir
- portable araç kütüphanesini büyütebilir
