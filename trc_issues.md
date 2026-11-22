# Trace file issues

## rocrail.003.trc

### Route not locked

| Count | First               | Last                | Message |
|------:|---------------------|---------------------|---------|
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:09 | `ORoute: route krt-ms is not locked` |
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:09 | `ORoute: route krt-mg is not locked` |
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:09 | `ORoute: route krt-gi is not locked` |
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:09 | `ORoute: route krt-gm is not locked` |
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:09 | `ORoute: route krt-gh is not locked` |
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:09 | `ORoute: route krt-si is not locked` |
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:09 | `ORoute: route krt-sm is not locked` |
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:09 | `ORoute: route krt-sh is not locked` |
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:09 | `ORoute: route krt-is is not locked` |
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:09 | `ORoute: route krt-ig is not locked` |
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:09 | `ORoute: route krt-hs is not locked` |
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:09 | `ORoute: route krt-hg is not locked` |

### Output without address

| Count | First               | Last                | Message |
|------:|---------------------|---------------------|---------|
|    12 | 2026-11-19 23:24:58 | 2026-11-19 23:25:10 | `OOutput: Output [krt-busy] has no address set; Skip command.` |
|    11 | 2026-11-19 23:24:59 | 2026-11-19 23:25:10 | `OOutput: Output [koCtl] has no address set; Skip command.` |

### Connection problem

| Count | First               | Last                | Message |
|------:|---------------------|---------------------|---------|
|     1 | 2026-11-19 23:24:59 | 2026-11-19 23:24:59 | `OSocket: *broken* errno=0, rc=10054, read=-1` |

### Unregistered sensor (address not in plan)

| Count | First               | Last                | Message |
|------:|---------------------|---------------------|---------|
|     2 | 2026-11-19 23:24:59 | 2026-11-19 23:25:01 | `OModel: unregistered sensor event: [xpr] 0:792 uidname=[]` |
|     2 | 2026-11-19 23:24:59 | 2026-11-19 23:25:01 | `OModel: unregistered sensor event: [xpr] 0:793 uidname=[]` |

## rocview.002.trc

### Manual signal change by operator

| Count | First               | Last                | Message |
|------:|---------------------|---------------------|---------|
|     4 | 2026-11-19 22:30:16 | 2026-11-19 22:30:33 | `app: sendToRocrail( <sg id="is09" cmd="flip" aspect="-1" controlcode="" slavecode=""/>` |
|     3 | 2026-11-19 23:09:01 | 2026-11-19 23:09:04 | `app: sendToRocrail( <sg id="ys01" cmd="flip" aspect="-1" controlcode="" slavecode=""/>` |
|     1 | 2026-11-19 23:17:46 | 2026-11-19 23:17:46 | `app: sendToRocrail( <sg id="is10" cmd="flip" aspect="-1" controlcode="" slavecode=""/>` |

### Manual sensor change by operator

| Count | First               | Last                | Message |
|------:|---------------------|---------------------|---------|
|     2 | 2026-11-19 23:08:44 | 2026-11-19 23:21:51 | `app: sendToRocrail( <fb id="id16" state="true" controlcode="" slavecode=""/>` |
|     2 | 2026-11-19 23:08:58 | 2026-11-19 23:21:57 | `app: sendToRocrail( <fb id="id16" state="false" controlcode="" slavecode=""/>` |
|     1 | 2026-11-19 23:14:29 | 2026-11-19 23:14:29 | `app: sendToRocrail( <fb id="id20" state="false" controlcode="" slavecode=""/>` |
|     1 | 2026-11-19 23:21:54 | 2026-11-19 23:21:54 | `app: sendToRocrail( <fb id="id17" state="true" controlcode="" slavecode=""/>` |
|     1 | 2026-11-19 23:21:56 | 2026-11-19 23:21:56 | `app: sendToRocrail( <fb id="id17" state="false" controlcode="" slavecode=""/>` |

### Manual output change by operator

| Count | First               | Last                | Message |
|------:|---------------------|---------------------|---------|
|     1 | 2026-11-19 23:17:04 | 2026-11-19 23:17:04 | `app: sendToRocrail( <co id="koRTip" value="0" cmd="flip" controlcode="" slavecode="">` |

### Warning

| Count | First               | Last                | Message |
|------:|---------------------|---------------------|---------|
|     1 | 2026-11-19 23:24:59 | 2026-11-19 23:24:59 | `app: Exit` |
|     1 | 2026-11-19 23:24:59 | 2026-11-19 23:24:59 | `frame: remove throttles from New...` |
|     1 | 2026-11-19 23:24:59 | 2026-11-19 23:24:59 | `frame: model=271E1A14` |
|     1 | 2026-11-19 23:24:59 | 2026-11-19 23:24:59 | `frame: lclist=2A8EAEB4` |
|     1 | 2026-11-19 23:24:59 | 2026-11-19 23:24:59 | `frame: check 3 locos for throttles` |
|     1 | 2026-11-19 23:24:59 | 2026-11-19 23:24:59 | `frame: throttle position: none found for [IC232]` |
|     1 | 2026-11-19 23:24:59 | 2026-11-19 23:24:59 | `frame: throttle position: none found for [GP60]` |
|     1 | 2026-11-19 23:24:59 | 2026-11-19 23:24:59 | `frame: throttle position: none found for [Nohab]` |
|     1 | 2026-11-19 23:25:01 | 2026-11-19 23:25:01 | `app: Exit already in progress...` |

### Connection problem

| Count | First               | Last                | Message |
|------:|---------------------|---------------------|---------|
|     1 | 2026-11-19 23:24:59 | 2026-11-19 23:24:59 | `ORCon: disconnect from server` |
|     1 | 2026-11-19 23:24:59 | 2026-11-19 23:24:59 | `ORCon: server info reader ended` |

## Interpretation

This section was written by hand. Running `trc_issues.py` again overwrites the file, so copy this section first.

1. **Coverage.** `rocrail.003.trc` covers only 12 seconds (23:24:58 to 23:25:10), when the session was shut down. The Rocrail server traces for the rest of the session aren't here. `rocview.002.trc` covers 21:25 to 23:25.
2. **Unregistered sensors 792 and 793.** In `DMJK-Adresser.pdf`, these are "Ledig" (free) on Sigdal RS-16-O i#3, ports 9 and 10 (RS address 99). This is the same module as id16-id21, the route and signal control sensors towards Myra. Inputs that should be free report "on". Possible causes are a wiring error, a new sensor that isn't in the plan, or a fault on the module. Check this on the Sigdal - Myra stretch.
3. **Route requests and manual signal changes on Sigdal - Myra.** Between 23:08 and 23:22, the operator set sensors id16, id17 and id20 from Rocview. These sensors are panel control inputs, not track detectors: id16 requests an exit towards Myra (sets `ioUTy`), id17 an entry from Myra (sets `ioINy`) and id20 the direction towards g. Setting them from Rocview is how the panel buttons are simulated, so this looks like testing the route. The operator also flipped signal ys01 3 times. That is a manual override. ys01 is on Myra block yd08, the same block as is03, whose port2 is wrong. Earlier, at 22:30 and 23:17, is09 and is10 were flipped by hand.
4. **Outputs without address** (`krt-busy`, `koCtl`): Rocrail skips the command. These look like virtual helper outputs used by actions, so this is probably by design.
5. **"Route ... is not locked"**: debug messages from action conditions during shutdown. Not an error.
6. **Socket `*broken*` rc=10054, "disconnect from server", throttle warnings, "Exit"**: all at 23:24:59, when Rocview closed. Normal shutdown.
7. **`koOccTmr`**: Rocview logs 239 updates of this variable during the session. It is a runtime timer, so the change from 21 to 5 in `analysis1.md` section 3 is runtime state, not configuration.
