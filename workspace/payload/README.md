# Workspace Payload

Bu klasör, rebuild öncesi workspace veya USB düzenine merge edilecek ek içeriği tanımlar.

Geçerli kaynak kökler:

- `workspace/payload/Desktop`
  `Users\\Public\\Desktop` hedefine gider
- `workspace/payload/ProgramFiles`
  `Program Files` altına merge edilir
- `workspace/payload/Users`
  `Users` ağacına merge edilir
- `workspace/payload/Tools`
  USB kökündeki `tools/` klasörüne merge edilir

Bu klasör artık legacy ikili payload yapıları kullanmaz.
