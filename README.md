# Focker 2

```diff
- IMPORTANT BACKWARDS INCOMPATIBLE CHANGE
-
- Focker now uses its own service to start the jails on boot. Use:
- focker bootstrap filesystem to create the new necessary filesystem
- (/focker/jailconf). Use scripts/migrate_jailconf.py to migrate your
- jail configs to the new location. Furthermore, you need to place and
- enable scripts/focker_service in /usr/local/etc/rc.d/.
```

________________

## This is a modified version of focker to be used with https://ttea.dev/t2v/fockerfiles
## Please refer to the original repository for documentation
