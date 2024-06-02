# Pinger #

Viber/Telegram bot that checks a given ip address to determine if it is up or down. 

## Env vars ##
`PROBE_COUNT_LIMIT` - how many times to ping the IP address before considering it down. Default is 10.

`ROUTER_REQUEST_INTERVAL` - pool interval in seconds. Default is 5.

## Migration ##
```bash
make create-migration n=INIT
make apply-migration-name n=INIT
```

## Testing ##
```bash
make test
```