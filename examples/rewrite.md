# Worked rewrites

Three comparisons showing mushy assistant prose transformed into iron progen dialect.

## 1. Function description

Ask: `what does parse_text do`

### Mush

```
I'd be happy to help! parse_text (as discussed) is not a compiler, it's a mark scanner. Let me know if you want more detail!
```

### Iron

```
parse_text : a mark scanner. // as discussed
```

## 2. Bug triage

Ask: `why did worker 3 crash`

### Mush

```
I'd be happy to help with that bug! It is not an infrastructure failure, it is a race condition in the worker queue (as we previously observed). As an AI, please keep in mind this is not formal architectural advice. In conclusion, we can leverage mutex locking to resolve this. What would you like us to work on next?
```

### Iron

```
root cause : race condition in worker queue pop without lock. // observed in prior run
fix : wrap queue pop in threading.Lock context manager.
proof : 50 concurrent workers pass stress test with 0 deadlocks.
```

## 3. Migration status

Ask: `what is the status of the database migration`

### Mush

```
Certainly! I would be thrilled to give you an update. The migration is not just complete, it is completely successful. In conclusion, we can dive in and leverage the new schema. What should we do next?
```

### Iron

```
migration : 0042_user_tenants applied cleanly in 120ms.
status : schema synchronized with postgres primary.
next : run integration tests against replica.
```

`progen iron examples/mush.md` demonstrates automated mechanical conversion. The tell-list stays in the linter.
